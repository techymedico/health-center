package com.iitj.healthcenter.domain.model

data class DoctorSchedule(
    val id: Int,
    val date: String,
    val name: String,
    val timing: String,
    val category: String,
    val room: String?
)
