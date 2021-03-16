package com.darcangel.wherediputthat

import android.os.Bundle
import android.util.Log
import com.google.android.material.floatingactionbutton.FloatingActionButton
import com.google.android.material.snackbar.Snackbar
import com.google.android.material.tabs.TabLayout
import androidx.viewpager.widget.ViewPager
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.LiveData
import com.darcangel.wherediputthat.database.AppDatabase
import com.darcangel.wherediputthat.database.Category
import com.darcangel.wherediputthat.ui.main.SectionsPagerAdapter
import io.reactivex.Scheduler
import io.reactivex.Single
import io.reactivex.schedulers.Schedulers

class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        val sectionsPagerAdapter = SectionsPagerAdapter(this, supportFragmentManager)
        val viewPager: ViewPager = findViewById(R.id.view_pager)
        viewPager.adapter = sectionsPagerAdapter
        val tabs: TabLayout = findViewById(R.id.tabs)
        tabs.setupWithViewPager(viewPager)
        val fab: FloatingActionButton = findViewById(R.id.fab)

        fab.setOnClickListener { view ->
            Snackbar.make(view, "Replace with your own action", Snackbar.LENGTH_LONG)
                    .setAction("Action", null).show()
        }

        //Initialize the DB
//        Log.d("categories", "items = $categoryList")
    }

    public fun thread(start: Boolean = true,
                      isDaemon: Boolean = false,
                      contextClassLoader: ClassLoader? = null,
                      name: String? = null,
                      priority: Int = -1,
                      block: () -> Unit): Thread {
        val appDatabase : AppDatabase = AppDatabase.getInstance(this)
        val cat : Category = Category("Home")
        appDatabase.getCategoryDao().addCategory(cat)
        val categoryList : List<Category> = appDatabase.getCategoryDao().getAllCategories()
    }
}