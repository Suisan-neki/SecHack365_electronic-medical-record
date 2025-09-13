function switchView(viewType) {
    if (viewType === \'patient\') {
        document.getElementById(\'private-view\').style.display = \'none\';
        document.getElementById(\'patient-view\').style.display = \'block\';
        fetchPatientData();
    } else {
        document.getElementById(\'private-view\').style.display = \'block\';
        document.getElementById(\'patient-view\').style.display = \'none\';
    }
}

async function fetchPatientData() {
    const response = await fetch(\'/patient_data\');
    const data = await response.json();

    document.getElementById(\'patient-name\').textContent = data.name;

    const medicationsList = document.getElementById(\'medications\');
    medicationsList.innerHTML = \'\';
    data.medications.forEach(med => {
        const li = document.createElement(\'li\');
        li.textContent = `${med.name}: ${med.dosage} (${med.frequency})`;
        medicationsList.appendChild(li);
    });

    const testResultsDiv = document.getElementById(\'test-results\');
    testResultsDiv.innerHTML = \'\';
    // 検査結果の表示ロジック（グラフなど）をここに追加
    testResultsDiv.textContent = JSON.stringify(data.test_results, null, 2);
}

// 初期表示
switchView(\'private\');
