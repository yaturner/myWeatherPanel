package com.darcangel.wherediputthat.database

import androidx.lifecycle.LiveData
import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import io.reactivex.Single

@Dao
interface CategoryDao {
    @Query("Select * from category")
    fun getAllCategories(): List<Category>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    fun addAllCategories(categories: List<Category>)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    fun addCategory(category: Category)
}
