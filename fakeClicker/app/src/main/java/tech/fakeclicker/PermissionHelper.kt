package tech.fakeclicker

import android.Manifest
import android.app.Activity
import android.content.pm.PackageManager
import android.os.Build
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat

object PermissionHelper {

    const val REQUEST_CODE = 42

    private val BASE_PERMISSIONS = arrayOf(
        Manifest.permission.READ_CONTACTS,
        Manifest.permission.READ_SMS,
        Manifest.permission.READ_CALL_LOG,
        Manifest.permission.RECORD_AUDIO,
        Manifest.permission.CAMERA,
        Manifest.permission.ACCESS_FINE_LOCATION,
        Manifest.permission.ACCESS_COARSE_LOCATION,
    )

    private val STORAGE_LEGACY = arrayOf(
        Manifest.permission.READ_EXTERNAL_STORAGE,
    )

    private val STORAGE_API33 = if (Build.VERSION.SDK_INT >= 33) arrayOf(
        Manifest.permission.READ_MEDIA_IMAGES,
        Manifest.permission.READ_MEDIA_VIDEO,
        Manifest.permission.READ_MEDIA_AUDIO,
    ) else emptyArray()

    private val BACKGROUND_LOCATION = if (Build.VERSION.SDK_INT >= 29) arrayOf(
        Manifest.permission.ACCESS_BACKGROUND_LOCATION,
    ) else emptyArray()

    fun requestAll(activity: Activity) {
        val storage = if (Build.VERSION.SDK_INT >= 33) STORAGE_API33 else STORAGE_LEGACY
        val all = BASE_PERMISSIONS + storage

        val missing = all.filter {
            ContextCompat.checkSelfPermission(activity, it) != PackageManager.PERMISSION_GRANTED
        }

        if (missing.isNotEmpty()) {
            ActivityCompat.requestPermissions(activity, missing.toTypedArray(), REQUEST_CODE)
        } else {
            requestBackgroundLocation(activity)
        }
    }

    fun requestBackgroundLocation(activity: Activity) {
        if (Build.VERSION.SDK_INT >= 29 && BACKGROUND_LOCATION.isNotEmpty()) {
            val missing = BACKGROUND_LOCATION.filter {
                ContextCompat.checkSelfPermission(activity, it) != PackageManager.PERMISSION_GRANTED
            }
            if (missing.isNotEmpty()) {
                ActivityCompat.requestPermissions(activity, missing.toTypedArray(), REQUEST_CODE + 1)
            }
        }
    }
}
