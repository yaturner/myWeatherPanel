package com.darcangel.wherediputthat.workers

import android.content.Context
import android.util.Log
import androidx.work.CoroutineWorker
import androidx.work.WorkerParameters
import com.darcangel.wherediputthat.database.AppDatabase
import com.darcangel.wherediputthat.database.Category
import com.darcangel.wherediputthat.utilities.CATEGORY_DATA_FILENAME
import com.google.gson.Gson
import kotlinx.coroutines.coroutineScope
import com.google.gson.reflect.TypeToken


class SeedCategoryDatabaseWorker(
    context : Context,
    workerParams : WorkerParameters) : CoroutineWorker(context, workerParams) {
    private val TAG by lazy { SeedCategoryDatabaseWorker::class.java.simpleName }

    override suspend fun doWork(): Result = coroutineScope {
        try {
            applicationContext.assets.open(CATEGORY_DATA_FILENAME).use { inputStream ->
                com.google.gson.stream.JsonReader(inputStream.reader()).use { jsonReader ->
                    val categoryType = object : TypeToken<List<Category>>() {}.type
                    val categoryList: List<Category> = Gson().fromJson(jsonReader, categoryType)

                    val database = AppDatabase.getInstance(applicationContext)
                    database.getCategoryDao().addAllCategories(categoryList)

                    Result.success()
                }
            }
        } catch (ex: Exception) {
            Log.e(TAG, "Error seeding database", ex)
            Result.failure()
        }
    }
}