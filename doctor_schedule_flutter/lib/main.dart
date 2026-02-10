import 'dart:convert';

import 'package:device_info_plus/device_info_plus.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:intl/intl.dart';
import 'package:provider/provider.dart';

/// Internal helper for parsed duty time range.
class _DutyTimeRange {
  final DateTime start;
  final DateTime end;

  const _DutyTimeRange(this.start, this.end);
}

/// Backend base URL (same as the existing Android app)
const String kBaseUrl = 'https://iitj-doctor-schedule-api.onrender.com/';

/// Simple model for a doctor schedule entry.
class DoctorSchedule {
  final int id;
  final String date;
  final String name;
  final String timing;
  final String category;
  final String? room;

  DoctorSchedule({
    required this.id,
    required this.date,
    required this.name,
    required this.timing,
    required this.category,
    this.room,
  });

  factory DoctorSchedule.fromJson(Map<String, dynamic> json) {
    return DoctorSchedule(
      id: json['id'] as int,
      date: json['date'] as String,
      name: json['name'] as String,
      timing: json['timing'] as String,
      category: json['category'] as String,
      room: json['room'] as String?,
    );
  }

  /// Heuristic: treat rows mentioning 'specialist' or 'visiting'
  /// as specialist doctors, everything else as regular/dentist.
  bool get isSpecialist {
    final lower = category.toLowerCase();
    return lower.contains('specialist') || lower.contains('visiting');
  }

  /// Returns true if this doctor is currently on duty, based on today's date
  /// and the time range in the `timing` field (e.g. "03:30 PM to 07:00 PM").
  bool isOnDutyNow(DateTime now) {
    // Date in API looks like "31/01/2026 SATURDAY" – we only match the prefix.
    final todayStr = DateFormat('dd/MM/yyyy').format(now);
    final yesterdayStr = DateFormat('dd/MM/yyyy').format(now.subtract(const Duration(days: 1)));
    
    final text = timing.replaceAll('–', '-');
    final range = _parseTimeRange(text, now);
    if (range == null) return false;
    
    var start = range.start;
    var end = range.end;
    final isOvernight = end.isBefore(start);
    
    // Check if duty date matches today
    if (date.startsWith(todayStr)) {
      // Handle rare overnight ranges (end next day).
      if (isOvernight) {
        end = end.add(const Duration(days: 1));
      }
      return !now.isBefore(start) && !now.isAfter(end);
    }
    
    // Check if duty date matches yesterday AND it's an overnight duty
    if (date.startsWith(yesterdayStr) && isOvernight) {
      // For overnight duty from yesterday, adjust times to yesterday's context
      final yesterday = now.subtract(const Duration(days: 1));
      start = DateTime(yesterday.year, yesterday.month, yesterday.day, start.hour, start.minute);
      end = DateTime(now.year, now.month, now.day, end.hour, end.minute);
      return !now.isBefore(start) && !now.isAfter(end);
    }
    
    return false;
  }

  /// Returns true if this duty has already ended for today.
  bool isPastDuty(DateTime now) {
    final todayStr = DateFormat('dd/MM/yyyy').format(now);
    final yesterdayStr = DateFormat('dd/MM/yyyy').format(now.subtract(const Duration(days: 1)));
    
    final range = _parseTimeRange(timing.replaceAll('–', '-'), now);
    if (range == null) return false;
    
    var end = range.end;
    final isOvernight = end.isBefore(range.start);
    
    // Check if duty date matches today
    if (date.startsWith(todayStr)) {
      if (isOvernight) {
        end = end.add(const Duration(days: 1));
      }
      return now.isAfter(end);
    }
    
    // Check if duty date matches yesterday AND it's an overnight duty
    if (date.startsWith(yesterdayStr) && isOvernight) {
      // For overnight duty from yesterday, end time is on today
      end = DateTime(now.year, now.month, now.day, end.hour, end.minute);
      return now.isAfter(end);
    }
    
    return false;
  }

  /// Returns true if this duty is later today (upcoming but not started).
  bool isUpcomingDuty(DateTime now) {
    final todayStr = DateFormat('dd/MM/yyyy').format(now);
    if (!date.startsWith(todayStr)) {
      // For non-today dates, treat as upcoming.
      return true;
    }
    final range = _parseTimeRange(timing.replaceAll('–', '-'), now);
    if (range == null) return false;
    var start = range.start;
    var end = range.end;
    if (end.isBefore(start)) {
      end = end.add(const Duration(days: 1));
    }
    return now.isBefore(start);
  }

  /// Internal helper to parse the time range from the timing string.
  _DutyTimeRange? _parseTimeRange(String text, DateTime now) {
    RegExpMatch? match;
    DateTime start;
    DateTime end;

    // Case 1: timing has AM/PM (12-hour format)
    if (text.toUpperCase().contains('AM') || text.toUpperCase().contains('PM')) {
      match = RegExp(
        r'(\d{1,2}:\d{2}\s*(AM|PM))\s*(?:-|to)\s*(\d{1,2}:\d{2}\s*(AM|PM))',
        caseSensitive: false,
      ).firstMatch(text);
      if (match == null) return null;

      final startStr = match.group(1)!;
      final endStr = match.group(3)!;
      final df = DateFormat('hh:mm a');
      start = df.parse(startStr);
      end = df.parse(endStr);
    } else {
      // Case 2: pure 24-hour format like "08:00-14:00" or "20:00 - 08:00"
      match = RegExp(
        r'(\d{1,2}:\d{2})\s*-\s*(\d{1,2}:\d{2})',
      ).firstMatch(text);
      if (match == null) return null;

      final startStr = match.group(1)!;
      final endStr = match.group(2)!;
      final df = DateFormat('HH:mm');
      start = df.parse(startStr);
      end = df.parse(endStr);
    }

    start = DateTime(now.year, now.month, now.day, start.hour, start.minute);
    end = DateTime(now.year, now.month, now.day, end.hour, end.minute);

    return _DutyTimeRange(start, end);
  }
}

/// Which date filter is selected.
enum DateFilter { today, tomorrow, all }

/// ViewModel: loads schedules, manages subscriptions + FCM token.
class ScheduleViewModel extends ChangeNotifier {
  final http.Client _client;
  ScheduleViewModel({http.Client? client}) : _client = client ?? http.Client();

  final List<DoctorSchedule> _schedules = [];
  final Set<String> _subscribedDoctors = {};

  bool _isLoading = false;
  String? _error;
  DateFilter _dateFilter = DateFilter.today;

  String? _deviceId;
  String? _fcmToken;

  List<DoctorSchedule> get schedules => List.unmodifiable(_schedules);
  Set<String> get subscribedDoctors => _subscribedDoctors;
  bool get isLoading => _isLoading;
  String? get error => _error;
  DateFilter get dateFilter => _dateFilter;

  /// Initialize: Firebase, deviceId, FCM token, subscriptions and initial data.
  Future<void> initialize() async {
    try {
      _setLoading(true);

      // Ensure Firebase is initialized (uses native google-services.json on Android)
      await Firebase.initializeApp();

      // Ask notification permission (Android 13+ and as a no-op on lower)
      await FirebaseMessaging.instance.requestPermission();

      // Get / create a stable deviceId based on Android ID (or a fallback)
      await _initDeviceId();

      // Get FCM token and register with backend
      await _initFcmToken();

      // Load current subscriptions from backend
      await _loadSubscriptions();

      // Load schedules with default filter (today)
      await loadSchedulesForFilter(_dateFilter);
    } catch (e) {
      _setError('Failed to initialize: $e');
    } finally {
      _setLoading(false);
    }
  }

  Future<void> _initDeviceId() async {
    if (_deviceId != null) return;
    final deviceInfo = DeviceInfoPlugin();
    try {
      final android = await deviceInfo.androidInfo;
      _deviceId = android.id;
    } catch (_) {
      _deviceId = 'unknown-device';
    }
  }

  Future<void> _initFcmToken() async {
    final token = await FirebaseMessaging.instance.getToken();
    _fcmToken = token;

    if (_deviceId != null && _fcmToken != null) {
      final uri = Uri.parse('${kBaseUrl}register-fcm-token');
      final body = jsonEncode({
        'device_id': _deviceId,
        'fcm_token': _fcmToken,
      });

      await _client.post(
        uri,
        headers: {'Content-Type': 'application/json'},
        body: body,
      );
    }

    // Listen for token refresh
    FirebaseMessaging.instance.onTokenRefresh.listen((newToken) async {
      _fcmToken = newToken;
      if (_deviceId != null) {
        final uri = Uri.parse('${kBaseUrl}register-fcm-token');
        final body = jsonEncode({
          'device_id': _deviceId,
          'fcm_token': _fcmToken,
        });
        await _client.post(
          uri,
          headers: {'Content-Type': 'application/json'},
          body: body,
        );
      }
    });
  }

  Future<void> _loadSubscriptions() async {
    if (_deviceId == null) return;
    final uri = Uri.parse('${kBaseUrl}subscriptions/$_deviceId');
    final resp = await _client.get(uri);
    if (resp.statusCode == 200) {
      final data = jsonDecode(resp.body) as Map<String, dynamic>;
      final List<dynamic> names = data['subscribed_doctors'] as List<dynamic>? ?? [];
      _subscribedDoctors
        ..clear()
        ..addAll(names.map((e) => e.toString()));
      notifyListeners();
    }
  }

  Future<void> loadSchedulesForFilter(DateFilter filter) async {
    _dateFilter = filter;
    _setLoading(true);
    _setError(null);
    try {
      _schedules.clear();
      
      if (filter == DateFilter.all) {
        // Fetch all schedules (no date filter)
        final uri = Uri.parse('${kBaseUrl}schedules');
        final resp = await _client.get(uri);
        if (resp.statusCode != 200) {
          throw Exception('Failed to load schedules (${resp.statusCode})');
        }
        final json = jsonDecode(resp.body) as Map<String, dynamic>;
        final List<dynamic> items = json['data'] as List<dynamic>? ?? [];
        _schedules.addAll(items.map((e) => DoctorSchedule.fromJson(e as Map<String, dynamic>)));
      } else {
        // For "today" or "tomorrow": fetch the target date + previous day to catch overnight duties
        final now = DateTime.now();
        final target = filter == DateFilter.today ? now : now.add(const Duration(days: 1));
        final dates = [
          DateFormat('dd/MM/yyyy').format(target.subtract(const Duration(days: 1))), // yesterday/today
          DateFormat('dd/MM/yyyy').format(target), // today/tomorrow
        ];
        
        // Fetch schedules for both dates
        final Set<int> seenIds = {};
        for (final dateParam in dates) {
          final uri = Uri.parse('${kBaseUrl}schedules').replace(
            queryParameters: {'date': dateParam},
          );
          final resp = await _client.get(uri);
          if (resp.statusCode == 200) {
            final json = jsonDecode(resp.body) as Map<String, dynamic>;
            final List<dynamic> items = json['data'] as List<dynamic>? ?? [];
            for (final item in items) {
              final schedule = DoctorSchedule.fromJson(item as Map<String, dynamic>);
              // Avoid duplicates (in case of overlapping data)
              if (!seenIds.contains(schedule.id)) {
                _schedules.add(schedule);
                seenIds.add(schedule.id);
              }
            }
          }
        }
      }
      
      notifyListeners();
    } catch (e) {
      _setError('Failed to load schedules: $e');
    } finally {
      _setLoading(false);
    }
  }

  Future<void> toggleSubscription(DoctorSchedule doctor) async {
    if (_deviceId == null) return;
    final isSubscribed = _subscribedDoctors.contains(doctor.name);
    final endpoint = isSubscribed ? 'unsubscribe-doctor' : 'subscribe-doctor';
    final uri = Uri.parse('$kBaseUrl$endpoint');

    final body = jsonEncode({
      'device_id': _deviceId,
      'doctor_name': doctor.name,
    });

    try {
      await _client.post(
        uri,
        headers: {'Content-Type': 'application/json'},
        body: body,
      );
      if (isSubscribed) {
        _subscribedDoctors.remove(doctor.name);
      } else {
        _subscribedDoctors.add(doctor.name);
      }
      notifyListeners();
    } catch (e) {
      _setError('Failed to update subscription: $e');
    }
  }

  /// Subscribe or unsubscribe all doctors in the provided list.
  Future<void> toggleNotifyAll(Iterable<DoctorSchedule> doctors) async {
    if (_deviceId == null) return;

    final names = doctors.map((d) => d.name).toSet();
    if (names.isEmpty) return;

    final allAlreadySubscribed = names.every(_subscribedDoctors.contains);
    final endpoint = allAlreadySubscribed ? 'unsubscribe-doctor' : 'subscribe-doctor';
    final uri = Uri.parse('$kBaseUrl$endpoint');

    try {
      for (final name in names) {
        final body = jsonEncode({
          'device_id': _deviceId,
          'doctor_name': name,
        });
        await _client.post(
          uri,
          headers: {'Content-Type': 'application/json'},
          body: body,
        );
        if (allAlreadySubscribed) {
          _subscribedDoctors.remove(name);
        } else {
          _subscribedDoctors.add(name);
        }
      }
      notifyListeners();
    } catch (e) {
      _setError('Failed to update all notifications: $e');
    }
  }

  void _setLoading(bool value) {
    _isLoading = value;
    notifyListeners();
  }

  void _setError(String? value) {
    _error = value;
    notifyListeners();
  }
}

/// Background message handler (required for Firebase Messaging).
@pragma('vm:entry-point')
Future<void> firebaseMessagingBackgroundHandler(RemoteMessage message) async {
  await Firebase.initializeApp();
}

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Register background handler before runApp
  FirebaseMessaging.onBackgroundMessage(firebaseMessagingBackgroundHandler);

  final viewModel = ScheduleViewModel();
  runApp(
    ChangeNotifierProvider.value(
      value: viewModel,
      child: const MyApp(),
    ),
  );

  // Kick off initialization without blocking the initial frame,
  // so the user sees the loading UI immediately.
  // ignore: unawaited_futures
  viewModel.initialize();
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'IITJ Doctor Schedule',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF667EEA)),
        useMaterial3: true,
      ),
      home: const ScheduleScreen(),
    );
  }
}

/// Main schedule screen with date filter and subscriptions.
class ScheduleScreen extends StatelessWidget {
  const ScheduleScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final vm = context.watch<ScheduleViewModel>();

    final regular = vm.schedules.where((d) => !d.isSpecialist).toList();
    final specialists = vm.schedules.where((d) => d.isSpecialist).toList();

    // Sort each list: on duty first, then upcoming, then completed.
    final now = DateTime.now();
    int compare(DoctorSchedule a, DoctorSchedule b) {
      final aOn = a.isOnDutyNow(now);
      final bOn = b.isOnDutyNow(now);
      if (aOn && !bOn) return -1;
      if (!aOn && bOn) return 1;

      final aUpcoming = a.isUpcomingDuty(now);
      final bUpcoming = b.isUpcomingDuty(now);
      if (aUpcoming && !bUpcoming) return -1;
      if (!aUpcoming && bUpcoming) return 1;

      return 0;
    }

    regular.sort(compare);
    specialists.sort(compare);

    final allDoctors = [...regular, ...specialists];
    final allSubscribed =
        allDoctors.isNotEmpty && allDoctors.every((d) => vm.subscribedDoctors.contains(d.name));

    return DefaultTabController(
      length: 2,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('Doctor Schedule'),
          centerTitle: true,
          bottom: const TabBar(
            indicatorSize: TabBarIndicatorSize.label,
            tabs: [
              Tab(text: 'Regular'),
              Tab(text: 'Specialists'),
            ],
          ),
        ),
        body: Container(
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: [
                const Color(0xFFEEF2FF),
                Colors.white,
              ],
              begin: Alignment.topCenter,
              end: Alignment.bottomCenter,
            ),
          ),
          child: Column(
            children: [
              const SizedBox(height: 8),
              _DateFilterChips(
                selected: vm.dateFilter,
                onChanged: (filter) {
                  vm.loadSchedulesForFilter(filter);
                },
              ),
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      'Tap a doctor to toggle notifications.',
                      style: Theme.of(context)
                          .textTheme
                          .bodySmall
                          ?.copyWith(color: Colors.grey[700]),
                    ),
                    if (allDoctors.isNotEmpty)
                      OutlinedButton.icon(
                        onPressed: () => vm.toggleNotifyAll(allDoctors),
                        icon: Icon(
                          allSubscribed
                              ? Icons.notifications_off_outlined
                              : Icons.notifications_active_outlined,
                          size: 18,
                        ),
                        label: Text(allSubscribed ? 'Mute all' : 'Notify all'),
                        style: OutlinedButton.styleFrom(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 10, vertical: 6),
                          visualDensity: VisualDensity.compact,
                        ),
                      ),
                  ],
                ),
              ),
              if (vm.isLoading)
                const Padding(
                  padding: EdgeInsets.symmetric(horizontal: 16),
                  child: LinearProgressIndicator(),
                ),
              if (vm.error != null)
                Padding(
                  padding: const EdgeInsets.all(12.0),
                  child: Column(
                    children: [
                      Text(
                        'Failed to load schedules.\n${vm.error}',
                        textAlign: TextAlign.center,
                        style: const TextStyle(color: Colors.red),
                      ),
                      const SizedBox(height: 8),
                      ElevatedButton.icon(
                        onPressed: () => vm.loadSchedulesForFilter(vm.dateFilter),
                        icon: const Icon(Icons.refresh),
                        label: const Text('Retry'),
                      ),
                    ],
                  ),
                ),
              if (vm.isLoading && allDoctors.isEmpty && vm.error == null)
                const Expanded(
                  child: Center(
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        CircularProgressIndicator(),
                        SizedBox(height: 12),
                        Text('Loading doctor schedules...'),
                      ],
                    ),
                  ),
                )
              else
              Expanded(
                child: TabBarView(
                  children: [
                    _DoctorList(
                      doctors: regular,
                      subscribedNames: vm.subscribedDoctors,
                      onToggleSubscription: vm.toggleSubscription,
                      emptyMessage:
                          'No regular doctors found for this day.',
                    ),
                    _DoctorList(
                      doctors: specialists,
                      subscribedNames: vm.subscribedDoctors,
                      onToggleSubscription: vm.toggleSubscription,
                      emptyMessage:
                          'No specialist doctors found for this day.',
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _DoctorList extends StatelessWidget {
  final List<DoctorSchedule> doctors;
  final Set<String> subscribedNames;
  final Future<void> Function(DoctorSchedule) onToggleSubscription;
  final String emptyMessage;

  const _DoctorList({
    required this.doctors,
    required this.subscribedNames,
    required this.onToggleSubscription,
    required this.emptyMessage,
  });

  @override
  Widget build(BuildContext context) {
    if (doctors.isEmpty) {
      return Center(
        child: Text(
          emptyMessage,
          style: Theme.of(context)
              .textTheme
              .bodyMedium
              ?.copyWith(color: Colors.grey[600]),
        ),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(12),
      itemCount: doctors.length,
      itemBuilder: (context, index) {
        final doctor = doctors[index];
        final isSubscribed = subscribedNames.contains(doctor.name);
        return _DoctorCard(
          doctor: doctor,
          isSubscribed: isSubscribed,
          onToggleSubscription: () => onToggleSubscription(doctor),
        );
      },
    );
  }
}

class _DateFilterChips extends StatelessWidget {
  final DateFilter selected;
  final ValueChanged<DateFilter> onChanged;

  const _DateFilterChips({
    required this.selected,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          ChoiceChip(
            label: const Text('Today'),
            selected: selected == DateFilter.today,
            onSelected: (_) => onChanged(DateFilter.today),
          ),
          const SizedBox(width: 8),
          ChoiceChip(
            label: const Text('Tomorrow'),
            selected: selected == DateFilter.tomorrow,
            onSelected: (_) => onChanged(DateFilter.tomorrow),
          ),
          const SizedBox(width: 8),
          ChoiceChip(
            label: const Text('All'),
            selected: selected == DateFilter.all,
            onSelected: (_) => onChanged(DateFilter.all),
          ),
        ],
      ),
    );
  }
}

class _DoctorCard extends StatelessWidget {
  final DoctorSchedule doctor;
  final bool isSubscribed;
  final VoidCallback onToggleSubscription;

  const _DoctorCard({
    required this.doctor,
    required this.isSubscribed,
    required this.onToggleSubscription,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final now = DateTime.now();
    final onDuty = doctor.isOnDutyNow(now);
    final pastDuty = doctor.isPastDuty(now);
    final upcomingDuty = !onDuty && !pastDuty && doctor.isUpcomingDuty(now);

    Color startColor;
    if (onDuty) {
      // Current duty: green highlight
      startColor = Colors.green.shade400.withOpacity(0.20);
    } else if (upcomingDuty) {
      // Upcoming duty: soft blue
      startColor = Colors.blue.shade400.withOpacity(0.16);
    } else if (pastDuty) {
      // Completed duty: soft red
      startColor = Colors.red.shade400.withOpacity(0.18);
    } else {
      // Fallback
      startColor = theme.colorScheme.primary.withOpacity(0.12);
    }

    final typeLabel =
        doctor.isSpecialist ? 'Specialist doctor' : 'Regular doctor';
    return Container(
      margin: const EdgeInsets.symmetric(vertical: 8),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(16),
        gradient: LinearGradient(
          colors: [
            startColor,
            onDuty ? Colors.white : Colors.white,
          ],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 8,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Material(
        color: Colors.transparent,
        borderRadius: BorderRadius.circular(16),
        child: InkWell(
          borderRadius: BorderRadius.circular(16),
          onTap: onToggleSubscription,
          child: Padding(
            padding: const EdgeInsets.all(14.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            doctor.name,
                            style: theme.textTheme.titleMedium?.copyWith(
                              fontWeight: FontWeight.w700,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Row(
                            children: [
                              Icon(
                                doctor.isSpecialist
                                    ? Icons.star_rate_rounded
                                    : Icons.person_rounded,
                                size: 18,
                                color: theme.colorScheme.primary,
                              ),
                              const SizedBox(width: 4),
                              Text(
                                typeLabel,
                                style: theme.textTheme.bodySmall?.copyWith(
                                  color: theme.colorScheme.primary,
                                  fontWeight: FontWeight.w500,
                                ),
                              ),
                            ],
                          ),
                          if (onDuty) ...[
                            const SizedBox(height: 6),
                            Container(
                              padding: const EdgeInsets.symmetric(
                                  horizontal: 8, vertical: 4),
                              decoration: BoxDecoration(
                                color: Colors.green.shade600,
                                borderRadius: BorderRadius.circular(999),
                              ),
                              child: Row(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  const Icon(
                                    Icons.circle,
                                    size: 10,
                                    color: Colors.white,
                                  ),
                                  const SizedBox(width: 4),
                                  Text(
                                    'On duty now',
                                    style: theme.textTheme.labelSmall
                                        ?.copyWith(color: Colors.white),
                                  ),
                                ],
                              ),
                            ),
                          ],
                        ],
                      ),
                    ),
                    const SizedBox(width: 8),
                    ElevatedButton.icon(
                      onPressed: onToggleSubscription,
                      icon: Icon(
                        isSubscribed
                            ? Icons.notifications_active
                            : Icons.notifications_none,
                        size: 18,
                      ),
                      label: Text(isSubscribed ? 'Subscribed' : 'Notify'),
                      style: ElevatedButton.styleFrom(
                        elevation: 0,
                        padding: const EdgeInsets.symmetric(
                            horizontal: 12, vertical: 8),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(999),
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                Row(
                  children: [
                    Icon(
                      Icons.calendar_today_outlined,
                      size: 16,
                      color: Colors.grey[700],
                    ),
                    const SizedBox(width: 6),
                    Flexible(
                      child: Text(
                        doctor.date,
                        style: theme.textTheme.bodySmall
                            ?.copyWith(color: Colors.grey[800]),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 6),
                Row(
                  children: [
                    Icon(
                      Icons.schedule_rounded,
                      size: 16,
                      color: Colors.grey[700],
                    ),
                    const SizedBox(width: 6),
                    Flexible(
                      child: Text(
                        doctor.timing,
                        style: theme.textTheme.bodySmall
                            ?.copyWith(color: Colors.grey[800]),
                      ),
                    ),
                  ],
                ),
                if ((doctor.room ?? '').isNotEmpty) ...[
                  const SizedBox(height: 6),
                  Row(
                    children: [
                      Icon(
                        Icons.meeting_room_rounded,
                        size: 16,
                        color: Colors.grey[700],
                      ),
                      const SizedBox(width: 6),
                      Flexible(
                        child: Text(
                          'Room: ${doctor.room}',
                          style: theme.textTheme.bodySmall
                              ?.copyWith(color: Colors.grey[800]),
                        ),
                      ),
                    ],
                  ),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }
}

