package com.darcangel.wherediputthat.database

import android.content.ClipData
import androidx.lifecycle.LiveData
import androidx.room.*
import io.reactivex.Single

@Dao
interface FindItItemDao {
    @Query("SELECT * FROM findit_item ORDER BY id")
    fun getAllItems(): List<FindItItem>


    @Query("SELECT * from findit_item where id = :showId")
    fun getItem(showId: Long): Single<FindItItem>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    fun addItem(findItItem : FindItItem) : Long

    @Delete
    fun deleteItem(findItItem : FindItItem)
}