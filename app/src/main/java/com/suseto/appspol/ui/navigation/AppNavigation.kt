package com.suseto.appspol.ui.navigation

import androidx.compose.runtime.Composable
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import com.suseto.appspol.ui.screens.DetailScreen
import com.suseto.appspol.ui.screens.HomeScreen

@Composable
fun AppNavigation() {
    val navController = rememberNavController()

    NavHost(
        navController = navController,
        startDestination = "home"
    ) {
        composable("home") {
            HomeScreen(navController = navController)
        }
        composable(
            route = "detail/{itemId}/{itemTitle}",
            arguments = listOf(
                navArgument("itemId") { type = NavType.StringType },
                navArgument("itemTitle") { type = NavType.StringType }
            )
        ) { backStackEntry ->
            val itemId = backStackEntry.arguments?.getString("itemId")
            val itemTitle = backStackEntry.arguments?.getString("itemTitle")
            DetailScreen(
                itemId = itemId,
                itemTitle = itemTitle,
                navController = navController
            )
        }
    }
}
