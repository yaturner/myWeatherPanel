package com.darcangel.wherediputthat.database

import java.sql.Date
import androidx.room.ColumnInfo
import androidx.room.Entity
import androidx.room.PrimaryKey
import java.time.LocalDate.now
import java.util.*

@Entity(tableName = "findit_item")
data class FindItItem(
    @PrimaryKey(autoGenerate=true) @ColumnInfo(name = "id") val id: Long,
    val category: String,
    val date: Calendar = Calendar.getInstance(),
    val frequency: String,
    val latitude: String,
    val longitude: String,
    val imageUri: String,
    val thumbnailUri: String
) {
    constructor() : this(-1, "", Calendar.getInstance(), "", "", "", "", "")
}
