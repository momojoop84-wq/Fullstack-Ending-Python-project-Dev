let currentPage = 1;
const limit = 5;

async function loadStudents(page = 1) {
    const tbody = document.getElementById("students-table-body");
    const msgArea = document.getElementById("message-area");
    const totalCount = document.getElementById("total-count");

    // Petit effet de chargement visuel (on vide le tableau)
    tbody.innerHTML = '<tr><td colspan="7" class="text-center py-4">Chargement...</td></tr>';

    try {
        const response = await fetch(`http://127.0.0.1:8000/etudiants?page=${page}&limit=${limit}`);
        
        if (!response.ok) throw new Error("Erreur API");
        
        const data = await response.json();
        
        // Mise à jour des compteurs
        totalCount.textContent = `Total affichés : ${data.data.length}`;
        
        // Rendu du tableau
        renderTable(data.data);
        updatePagination(data);
        
        currentPage = page;

    } catch (error) {
        console.error("Erreur:", error);
        tbody.innerHTML = '';
        msgArea.classList.remove("hidden");
        msgArea.textContent = "Erreur de connexion au serveur. Vérifie que uvicorn tourne.";
        msgArea.classList.add("text-red-500");
    }
}

function renderTable(students) {
    const tbody = document.getElementById("students-table-body");
    const msgArea = document.getElementById("message-area");
    
    tbody.innerHTML = ""; // Vider

    if (students.length === 0) {
        msgArea.classList.remove("hidden");
        msgArea.textContent = "Aucun étudiant à cette page.";
        return;
    } else {
        msgArea.classList.add("hidden");
    }

    students.forEach(student => {
        // Définition du style selon la source (Badges Tailwind)
        // DB = Vert, JSON = Jaune
        const sourceBadgeClass = student.source === 'DB' 
            ? 'bg-green-100 text-green-800' 
            : 'bg-yellow-100 text-yellow-800';
        
        // Création de la ligne HTML avec classes Tailwind
        const rowHTML = `
            <tr class="border-b border-gray-200 hover:bg-gray-50 transition duration-300">
                <td class="py-3 px-6 text-left whitespace-nowrap">
                    <span class="${sourceBadgeClass} py-1 px-3 rounded-full text-xs font-bold uppercase tracking-wide">
                        ${student.source}
                    </span>
                </td>
                <td class="py-3 px-6 text-left">
                    <span class="font-medium text-gray-900">${student.numero}</span>
                </td>
                <td class="py-3 px-6 text-left font-mono text-xs text-gray-500">${student.code}</td>
                <td class="py-3 px-6 text-left font-bold text-gray-700">${student.nom}</td>
                <td class="py-3 px-6 text-left">${student.prenom}</td>
                <td class="py-3 px-6 text-left">
                    <span class="bg-gray-200 text-gray-700 py-1 px-2 rounded text-xs">${student.classe || 'N/A'}</span>
                </td>
                <td class="py-3 px-6 text-center">
                    <span class="${getMoyenneColor(student.moyenne_generale)} font-bold">
                        ${student.moyenne_generale}/20
                    </span>
                </td>
            </tr>
        `;
        
        // On injecte le HTML brut (plus simple que createElement pour Tailwind)
        tbody.insertAdjacentHTML('beforeend', rowHTML);
    });
}

// Petite fonction utilitaire pour colorer la moyenne (Bonus)
function getMoyenneColor(moyenne) {
    if (moyenne >= 10) return "text-green-600";
    if (moyenne >= 8) return "text-orange-500";
    return "text-red-600";
}

function updatePagination(data) {
    document.getElementById("page-info").textContent = data.page;
    
    const btnPrev = document.getElementById("btn-prev");
    const btnNext = document.getElementById("btn-next");

    // Gestion des boutons
    btnPrev.disabled = data.page <= 1;
    
    // Si on a moins de résultats que la limite, on désactive le bouton suivant
    // (C'est une simplification, idéalement on vérifierait contre le total global)
    btnNext.disabled = data.data.length < limit;
}

// Gestionnaires d'événements
document.getElementById("btn-next").addEventListener("click", () => {
    loadStudents(currentPage + 1);
});

document.getElementById("btn-prev").addEventListener("click", () => {
    if (currentPage > 1) loadStudents(currentPage - 1);
});

// Démarrage
document.addEventListener("DOMContentLoaded", () => {
    loadStudents(1);
});