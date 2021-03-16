package com.darcangel.wherediputthat.viewmodels

import androidx.lifecycle.ViewModel
import com.darcangel.wherediputthat.database.Category
import java.util.*
import androidx.databinding.ObservableField

class CategoryViewModel(categories : Category) : ViewModel() {

    private val category = ObservableField<String>(checkNotNull(categories.category))
}