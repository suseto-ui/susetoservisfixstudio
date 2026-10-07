plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.kotlin.android)
    alias(libs.plugins.kotlin.compose)
}

android {
    namespace = "com.suseto.appspol"
    compileSdk = 36

    defaultConfig {
        applicationId = "com.suseto.appspol"
        minSdk = 24
        targetSdk = 36
        versionCode = 1
        versionName = "1.0.0"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_21
        targetCompatibility = JavaVersion.VERSION_21
    }
    kotlinOptions {
        jvmTarget = "21"
    }
    buildFeatures {
        compose = true
    }
}

dependencies {
    implementation(libs.androidx.core.ktx)
    implementation(libs.androidx.lifecycle.runtime.ktx)
    implementation(libs.androidx.activity.compose)
    implementation(platform(libs.androidx.compose.bom))
    implementation(libs.androidx.compose.ui)
    implementation(libs.androidx.compose.ui.graphics)
    implementation(libs.androidx.compose.ui.tooling.preview)
    implementation(libs.androidx.compose.material3)
    implementation(libs.androidx.navigation.compose)
}

// Custom Gradle task to automatically generate back navigation TopBar component
tasks.register("generateBackButtonComponent") {
    group = "generation"
    description = "Vygeneruje Jetpack Compose komponentu AppTopBar s funkcí popBackStack()"

    val targetDir = file("src/main/java/com/suseto/appspol/ui/components")
    val targetFile = file("${targetDir}/AppTopBar.kt")

    doLast {
        if (!targetDir.exists()) {
            targetDir.mkdirs()
        }
        targetFile.writeText(
            """
            package com.suseto.appspol.ui.components

            import androidx.compose.material.icons.Icons
            import androidx.compose.material.icons.automirrored.filled.ArrowBack
            import androidx.compose.material3.*
            import androidx.compose.runtime.Composable
            import androidx.navigation.NavController

            @OptIn(ExperimentalMaterial3Api::class)
            @Composable
            fun AppTopBar(
                title: String,
                navController: NavController
            ) {
                TopAppBar(
                    title = { Text(text = title) },
                    navigationIcon = {
                        IconButton(
                            onClick = { navController.popBackStack() }
                        ) {
                            Icon(
                                imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                                contentDescription = "Zpět"
                            )
                        }
                    },
                    colors = TopAppBarDefaults.topAppBarColors(
                        containerColor = MaterialTheme.colorScheme.primaryContainer,
                        titleContentColor = MaterialTheme.colorScheme.onPrimaryContainer
                    )
                )
            }
            """.trimIndent()
        )
        logger.lifecycle("-> Soubor AppTopBar.kt byl úspěšně vygenerován do: ${targetFile.path}")
    }
}
