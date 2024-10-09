async function handleFormSubmit(event) {
    event.preventDefault();

    const form = event.target;
    const formData = new FormData(form);

    // Show the spinner
    document.getElementById("spinner").style.display = "block";

    try {
        // Fetch the file and download it
        const response = await fetch('/generate_dqv_file/', {
            method: "POST",
            body: formData
        });

        if (response.ok) {
            const blob = await response.blob();
            const outputFormat = formData.get("output_format");
            const downloadUrl = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = downloadUrl;
            a.download = `output.${outputFormat}`;
            document.body.appendChild(a);
            a.click();
            a.remove();

            // Now fetch the summary data for visualization
            const summaryResponse = await fetch('/generate_dqv_summary/', {
                method: "POST",
                body: formData
            });

            if (summaryResponse.ok) {
                const summaryData = await summaryResponse.json();
                console.log("Summary Data:", summaryData);  // Log for debugging
                renderChart(summaryData);
            } else {
                const errorMessage = await summaryResponse.text();
                alert("Error fetching summary data: " + errorMessage);
            }
        } else {
            const errorMessage = await response.text();
            alert("Error downloading file: " + errorMessage);
        }
    } catch (error) {
        alert("Error occurred during the request: " + error.message);
    } finally {
        // Hide the spinner when the request is finished
        document.getElementById("spinner").style.display = "none";
    }
}

function renderChart(data) {
    const ctx = document.getElementById('evaluationChart').getContext('2d');

    // Check if a chart instance exists and destroy it before creating a new one
    if (window.evaluationChart instanceof Chart) {
        window.evaluationChart.destroy(); // Safely destroy the previous chart instance
    }

    // Render the new chart and save the instance to window.evaluationChart
    window.evaluationChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Findable', 'Accessible', 'Interoperable', 'Reusable'],
            datasets: [
                {
                    label: 'FES Scores',
                    backgroundColor: '#6A994E',
                    data: [
                        data.fes.findability_score ?? 0,
                        data.fes.accessibility_score ?? 0,
                        data.fes.interoperability_score ?? 0,
                        data.fes.reusability_score ?? 0
                    ]
                },
                {
                    label: 'FUJI Scores',
                    backgroundColor: '#FFD700',
                    data: [
                        data.fuji.findability_score ?? 0,
                        data.fuji.accessibility_score ?? 0,
                        data.fuji.interoperability_score ?? 0,
                        data.fuji.reusability_score ?? 0
                    ]
                }
            ]
        },
        options: {
            maintainAspectRatio: false,  // Keeps the chart responsive
            scales: {
                y: {
                    beginAtZero: true,
                    min: 0.0,
                    max: 1.0,
                    ticks: {
                        stepSize: 0.2  // Adjust to display even steps like 0.0, 0.2, 0.4, etc.
                    }
                }
            }
        }
    });
}
