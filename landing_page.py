from fastapi.responses import HTMLResponse


def get_landing_page() -> HTMLResponse:
    return HTMLResponse("""
    <html>
        <head>
            <title>FAIR-ER - The FAIR Evaluation Repository</title>
            <link rel="icon" type="image/x-icon" href="/static/favicon.ico">
            <style>
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
                    background-color: #007BFF;
                    color: white;
                    padding: 15px 25px;
                    font-size: 1.2em;
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                    text-align: center;
                    text-decoration: none;
                    transition: background-color 0.3s ease;
                }
                .btn:hover {
                    background-color: #0056b3;
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
                input[type="submit"] {
                    background-color: #007BFF;
                    color: white;
                    padding: 10px 20px;
                    font-size: 1.2em;
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                    transition: background-color 0.3s ease;
                }
                input[type="submit"]:hover {
                    background-color: #0056b3;
                }
                /* Styling for the favicon image */
                .favicon-container img {
                    width: 100px; /* Adjust the size as needed */
                    height: auto;
                    margin-top: 20px;
                }
                /* Label positioning to move it above the input field */
                label {
                    font-size: 1.2em;
                    font-weight: bold;
                    display: block;  /* Ensures the label is above the input field */
                    margin-bottom: 5px;
                }
                /* Progress bar styling */
                #loading {
                    display: none;
                    margin-top: 20px;
                    font-size: 1.5em;
                    color: #007BFF;
                }
                #loading-bar {
                    display: none;
                    width: 100%;  /* Set the width to be responsive */
                    max-width: 400px;  /* Maximum width of the bar */
                    height: 20px;
                    background-color: #f3f3f3;
                    border: 1px solid #007BFF;
                    border-radius: 10px;
                    overflow: hidden;
                    margin-top: 20px;
                    box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.2);
                }
                #loading-bar-progress {
                    width: 100%; /* Start full and decrease */
                    height: 100%;
                    background-color: #007BFF;
                    transition: width 0.3s ease;
                }
                .progress-text {
                    font-size: 1em;
                    color: #007BFF;
                    margin-top: 10px;
                }
            </style>
            <script>
                function startLoading() {
                    document.getElementById("loading").style.display = "block";
                    document.getElementById("loading-bar").style.display = "block";
                    document.getElementById("progress-text").style.display = "block";

                    let progress = 100;
                    const interval = setInterval(() => {
                        if (progress <= 0) {
                            clearInterval(interval);
                        } else {
                            progress -= 1;
                            document.getElementById("loading-bar-progress").style.width = progress + "%";
                        }
                    }, 300);  // 300ms * 100 = 30 seconds
                }
            </script>
        </head>
        <body>
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
                    <form action="/generate_dqv_file/" method="post" onsubmit="startLoading()">
                        <!-- Label is now correctly above the text field -->
                        <label for="doi">Enter DOI:</label>
                        <input type="text" id="doi" name="doi" value="10.5447/ipk/2017/2" required>
                        <br>
                        <input type="submit" class="btn" value="Generate and Download DQV File">
                    </form>
                    <div id="loading">Estimated processing time: 30 seconds</div>
                    <div id="loading-bar">
                        <div id="loading-bar-progress"></div>
                    </div>
                    <div id="progress-text" class="progress-text" style="display: none;">Processing, please wait...</div>
                </div>

                <footer>
                    <p>&copy; 2024 FAIR-ER. All rights reserved.</p>
                </footer>
            </div>
        </body>
    </html>
    """)
