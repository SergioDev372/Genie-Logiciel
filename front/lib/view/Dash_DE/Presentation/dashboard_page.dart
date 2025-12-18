import 'package:flutter/material.dart';
import '../widgets/dashboard_app_bar.dart';
import '../widgets/overview_card.dart';
import '../widgets/quick_action_button.dart';
import '../widgets/bottom_nav_bar.dart';

class DashboardPage extends StatelessWidget {
  const DashboardPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey.shade100,
      bottomNavigationBar: const DashboardBottomNavBar(),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const DashboardAppBar(),
              const SizedBox(height: 24),

              const Text(
                'Aperçu Général',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 16),

              GridView.count(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                crossAxisCount: 2,
                crossAxisSpacing: 16,
                mainAxisSpacing: 16,
                children: const [
                  OverviewCard(
                    icon: Icons.group,
                    value: '250',
                    label: 'Utilisateurs',
                  ),
                  OverviewCard(
                    icon: Icons.school,
                    value: '15',
                    label: 'Espaces Pédagogiques',
                  ),
                  OverviewCard(
                    icon: Icons.grid_view,
                    value: '8',
                    label: 'Promotions',
                  ),
                ],
              ),

              const SizedBox(height: 32),

              const Text(
                'Actions Rapides',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 16),

              QuickActionButton(
                label: 'Créer Promotion',
                onPressed: () {},
              ),
              const SizedBox(height: 12),
              QuickActionButton(
                label: 'Créer Espace Pédagogique',
                onPressed: () {},
              ),
            ],
          ),
        ),
      ),
    );
  }
}
