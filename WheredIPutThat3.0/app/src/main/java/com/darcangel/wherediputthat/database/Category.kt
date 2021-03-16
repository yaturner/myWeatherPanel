package com.darcangel.wherediputthat.database

import androidx.room.ColumnInfo;
import androidx.room.Entity;
import androidx.room.PrimaryKey;

@Entity(tableName="category")
data class Category(
    @PrimaryKey @ColumnInfo(name="category") val category: String
)  {
    constructor() : this("")
}
