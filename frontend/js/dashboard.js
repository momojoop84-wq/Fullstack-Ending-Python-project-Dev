async function loadDashboard() {
    try {
        // Récupérer les stats
        const response = await fetch("http://127.0.0.1:8000/stats");
        const stats = await response.json();

        // 1. Mettre à jour les KPI
        document.getElementById("kpi-db").textContent = stats.total_db;
        document.getElementById("kpi-json").textContent = stats.total_json;
        document.getElementById("kpi-total").textContent = stats.total_db + stats.total_json;

        // 2. Graphique Répartition Classes (Bar Chart)
        const ctxClasses = document.getElementById('chartClasses').getContext('2d');
        new Chart(ctxClasses, {
            type: 'bar',
            data: {
                labels: stats.repartition_classe.map(item => item.classe),
                datasets: [{
                    label: 'Nombre d\'étudiants',
                    data: stats.repartition_classe.map(item => item.count),
                    backgroundColor: 'rgba(54, 162, 235, 0.6)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }]
            },
            options: { responsive: true, maintainAspectRatio: false }
        });

        // 3. Graphique Moyennes (Line Chart)
        const ctxMoyennes = document.getElementById('chartMoyennes').getContext('2d');
        new Chart(ctxMoyennes, {
            type: 'line',
            data: {
                labels: stats.moyenne_par_classe.map(item => item.classe),
                datasets: [{
                    label: 'Moyenne /20',
                    data: stats.moyenne_par_classe.map(item => item.moyenne),
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 2,
                    tension: 0.3
                }]
            },
            options: { 
                responsive: true, 
                maintainAspectRatio: false,
                scales: { y: { beginAtZero: true, max: 20 } }
            }
        });

    } catch (error) {
        console.error("Erreur chargement dashboard :", error);
        alert("Impossible de charger les statistiques.");
    }
}

// Charger au démarrage
document.addEventListener("DOMContentLoaded", loadDashboard);