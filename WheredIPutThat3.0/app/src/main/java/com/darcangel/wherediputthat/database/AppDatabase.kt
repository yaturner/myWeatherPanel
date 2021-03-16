package com.darcangel.wherediputthat.database

import android.content.Context
import androidx.room.Database
import androidx.room.Room
import androidx.room.Room.databaseBuilder
import androidx.room.RoomDatabase
import androidx.room.TypeConverters
import androidx.sqlite.db.SupportSQLiteDatabase
import androidx.work.OneTimeWorkRequestBuilder
import androidx.work.WorkManager
import com.darcangel.wherediputthat.utilities.APP_DATABASE_NAME
import com.darcangel.wherediputthat.workers.SeedCategoryDatabaseWorker

@Database(entities = [FindItItem::class, Category::class], version=1, exportSchema = false)
@TypeConverters(Converters::class)
abstract class AppDatabase : RoomDatabase() {
    abstract fun getItemDao() : FindItItemDao
    abstract fun getCategoryDao() : CategoryDao

    companion object {
        @Volatile
        private var instance: AppDatabase? = null

        fun getInstance(context: Context): AppDatabase {
            return instance ?: synchronized(this) {
                instance ?: buildDatabase(context).also { instance = it }
            }
        }

        private fun buildDatabase(context : Context) : AppDatabase {
            return Room.databaseBuilder(context, AppDatabase::class.java, APP_DATABASE_NAME)
                .addCallback(object : RoomDatabase.Callback() {
                    override fun onCreate(db: SupportSQLiteDatabase) {
                        super.onCreate(db)
                        val request = OneTimeWorkRequestBuilder<SeedCategoryDatabaseWorker>().build()
                        WorkManager.getInstance().enqueue(request)
                    }
                }).build()
        }
    }
}