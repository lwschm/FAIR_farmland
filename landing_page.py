from fastapi.responses import HTMLResponse

def get_landing_page() -> HTMLResponse:
    return HTMLResponse("""
    <html>
        <head>
            <title>FAIR-ER - The FAIR Evaluation Repository</title>
            <link rel="icon" type="image/x-icon" href="/static/favicon.ico">
            <style>
                /* Top menu styling */
                .top-menu {
                    background-color: #6A994E;
                    padding: 10px 0;
                    text-align: center;
                }
                .top-menu a {
                    color: white;
                    text-decoration: none;
                    font-size: 1.2em;
                    margin: 0 15px;
                    font-weight: bold;
                }
                .top-menu a:hover {
                    text-decoration: underline;
                }
                body {
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                    background-color: #f4f4f4;
                    color: #333;
                }
                .container {
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                    text-align: center;
                }
                h1 {
                    font-size: 3em;
                    margin-bottom: 0.5em;
                }
                p {
                    font-size: 1.2em;
                    margin-bottom: 1.5em;
                    max-width: 600px;
                }
                .btn {
                    background-color: #6A994E !important;
                    color: white;
                    padding: 15px 25px;
                    font-size: 1.2em;
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                    text-align: center;
                    text-decoration: none;
                    transition: background-color 0.3s ease;
                    margin-top: 10px;  /* Adds spacing between dropdown and button */
                }
                .btn:hover {
                    background-color: #4d7a37 !important;
                }
                footer {
                    margin-top: 2em;
                    font-size: 0.9em;
                    color: #666;
                }
                input[type="text"] {
                    padding: 10px;
                    font-size: 1.2em;
                    width: 300px;
                    border: 2px solid #007BFF;
                    border-radius: 5px;
                    margin-bottom: 20px;
                }
                /* Form styling to vertically stack dropdown and button */
                form {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                }
                select {
                    padding: 10px;
                    font-size: 1.2em;
                    margin-bottom: 20px;
                    border: 2px solid #007BFF;
                    border-radius: 5px;
                    width: 300px;
                }
                input[type="submit"] {
                    background-color: #007BFF;
                    color: white;
                    padding: 10px 20px;
                    font-size: 1.2em;
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                    transition: background-color 0.3s ease;
                    margin-top: 10px;  /* Spacing between dropdown and button */
                }
                input[type="submit"]:hover {
                    background-color: #0056b3;
                }
                /* Centered label and checkboxes */
                .input-container label {
                    display: block;
                    text-align: center;
                    margin-bottom: 10px;
                    font-size: 1.2em;
                }
                .checkbox-group {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    margin-bottom: 15px;
                }
                .checkbox {
                    display: flex;
                    align-items: center;
                    justify-content: flex-start;
                    margin-bottom: 10px;
                    width: 200px;
                }
                .checkbox input {
                    transform: scale(1.5);
                    margin: 0;
                    vertical-align: middle;
                }
                .checkbox label {
                    margin-left: 10px;
                    font-size: 1.2em;
                    line-height: 1;
                    display: flex;
                    align-items: center;
                }
                /* Increased logo size */
                .favicon-container img {
                    width: 200px;
                    height: auto;
                    margin-top: 20px;
                }
                /* Spinner styling */
                .spinner-container {
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    margin-top: 20px;
                }

                .spinner {
                    display: none;
                    border: 6px solid #f3f3f3;
                    border-radius: 50%;
                    border-top: 6px solid #007BFF;
                    width: 40px;
                    height: 40px;
                    animation: spin 2s linear infinite;
                }

                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
            </style>
            <script>
                async function handleFormSubmit(event) {
                    event.preventDefault();  // Prevent the default form submission

                    const form = event.target;
                    const formData = new FormData(form);

                    // Show the spinner
                    document.getElementById("spinner").style.display = "block";

                    // Get the selected format
                    const outputFormat = formData.get("output_format");

                    // Fetch the file
                    try {
                        const response = await fetch(form.action, {
                            method: "POST",
                            body: formData
                        });

                        if (response.ok) {
                            const blob = await response.blob();
                            const downloadUrl = window.URL.createObjectURL(blob);
                            const a = document.createElement('a');
                            a.href = downloadUrl;
                            a.download = `output.${outputFormat}`;  // Set the downloaded file name dynamically
                            document.body.appendChild(a);
                            a.click();
                            a.remove();
                        } else {
                            alert("Error downloading file");
                        }
                    } catch (error) {
                        alert("Error occurred during the request.");
                    } finally {
                        // Hide the spinner when the request is finished
                        document.getElementById("spinner").style.display = "none";
                    }
                }
            </script>
        </head>
        <body>
             <!-- Top Menu -->
            <div class="top-menu">
                <a href="/">Home</a>
                <a href="https://github.com/fairagro/FAIR_evaluation_repository" target="_blank">GitHub</a>
                <a href="/docs" target="_blank" rel="noopener noreferrer">API</a>
            </div>
            <div class="container">
                <!-- Displaying the favicon at the top -->
                <div class="favicon-container">
                    <img src="/static/favicon_1024.ico" alt="FAIR-ER Logo">
                </div>
                <h1>Welcome to FAIR-ER</h1>
                <p>FAIR-ER, The FAIR Evaluation Repository, provides powerful tools to evaluate and interact with datasets.
                   Use our API to retrieve dataset information, perform FAIR metrics evaluations, and assess the quality of resources using DOIs.
                   Enter a DOI below to generate and download a FAIR evaluation file.</p>

                <div class="input-container">
                    <form action="/generate_dqv_file/" method="post" onsubmit="handleFormSubmit(event)">
                        <label for="doi">Enter DOI:</label>
                        <input type="text" id="doi" name="doi" value="10.5447/ipk/2017/2" required>

                        <!-- Hidden fields to send "false" when unchecked -->
                        <input type="hidden" name="fes" value="false">
                        <input type="hidden" name="fuji" value="false">

                        <!-- Checkboxes for evaluation services -->
                        <div class="checkbox-group">
                            <div class="checkbox">
                                <input type="checkbox" id="fes" name="fes" value="true" checked>
                                <label for="fes">Use FES Evaluation</label>
                            </div>
                            <div class="checkbox">
                                <input type="checkbox" id="fuji" name="fuji" value="true" checked>
                                <label for="fuji">Use FUJI Evaluation</label>
                            </div>
                        </div>

                        <!-- Dropdown for output format, centered above button -->
                        <label for="output_format">Select Output Format:</label>
                        <select id="output_format" name="output_format">
                            <option value="ttl">Turtle</option>
                            <option value="jsonld">JSON-LD</option>
                        </select>

                        <!-- Button placed below dropdown -->
                        <input type="submit" class="btn" value="Generate and Download DQV File">
                    </form>

                    <!-- Spinner for loading -->
                    <div class="spinner-container">
                        <div id="spinner" class="spinner"></div>
                    </div>
                </div>

                <footer>
                    <p>&copy; 2024 FAIR-ER. All rights reserved.</p>
                </footer>
            </div>
        </body>
    </html>
    """)
