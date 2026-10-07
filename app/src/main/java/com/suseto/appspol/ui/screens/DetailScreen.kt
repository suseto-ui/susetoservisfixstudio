package com.suseto.appspol.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.navigation.NavController
import com.suseto.appspol.ui.components.AppTopBar

@Composable
fun DetailScreen(
    itemId: String?,
    itemTitle: String?,
    navController: NavController
) {
    Scaffold(
        topBar = {
            AppTopBar(
                title = itemTitle ?: "Detail položky",
                navController = navController
            )
        }
    ) { paddingValues ->
        Surface(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues),
            color = MaterialTheme.colorScheme.background
        ) {
            Column(
                modifier = Modifier.padding(24.dp)
            ) {
                Text(
                    text = "ID Položky: ${itemId ?: "Neznámé"}",
                    style = MaterialTheme.typography.labelLarge,
                    color = MaterialTheme.colorScheme.primary
                )
                Spacer(modifier = Modifier.height(12.dp))
                Text(
                    text = itemTitle ?: "Neznámý název",
                    style = MaterialTheme.typography.headlineMedium,
                    color = MaterialTheme.colorScheme.onBackground
                )
                Spacer(modifier = Modifier.height(16.dp))
                Text(
                    text = "Tato obrazovka zobrazuje kompletní parametry a provozní metriky vybraného objektu z lokální databáze AndroidServiceStudio.",
                    style = MaterialTheme.typography.bodyLarge,
                    color = MaterialTheme.colorScheme.onBackground.copy(alpha = 0.8f)
                )
            }
        }
    }
}
