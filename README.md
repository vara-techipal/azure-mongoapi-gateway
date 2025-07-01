<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Azure MongoDB Atlas API Gateway</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }
    h1, h2, h3 { color: #333; }
    pre { background: #f4f4f4; padding: 10px; overflow-x: auto; }
    code { background: #f4f4f4; padding: 2px 4px; border-radius: 4px; }
    table { border-collapse: collapse; width: 100%; margin: 20px 0; }
    th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
    th { background: #eaeaea; }
    hr { border: none; border-top: 1px solid #ddd; margin: 30px 0; }
  </style>
</head>
<body>
  <h1>Azure MongoDB Atlas API Gateway</h1>
  <p>A serverless HTTP API gateway built with Azure Functions, providing secure, customizable access to your MongoDB Atlas collections. This tool replaces MongoDB’s deprecated Data API and custom HTTPS endpoints (fully retired on <strong>September 30, 2025</strong>).</p>
  <hr>
  <h2>Why I Built It</h2>
  <p>MongoDB Atlas removed support for its built-in REST API for new customers in June 2025, with complete removal scheduled for <strong>September 30, 2025</strong>. Many applications and integrations relied on simple HTTP calls to Atlas, so this gateway restores that functionality via a lightweight, serverless function.</p>
  <hr>
  <h2>What It Does</h2>
  <ul>
    <li><strong>Dynamic Routing</strong>: Accepts HTTP requests with the following query parameters:
      <ul>
        <li><code>db</code>: target database name</li>
        <li><code>coll</code>: target collection name</li>
        <li><code>id</code> <em>(optional)</em>: a document’s ObjectId for single-record fetches</li>
      </ul>
    </li>
    <li><strong>GET Support</strong>: Lists up to 100 documents when no <code>id</code> is provided; returns a single document when <code>id</code> is specified.</li>
    <li><strong>Type Conversion</strong>: Converts MongoDB BSON types (e.g. <code>_id</code>, <code>Date</code>) into JSON-serializable strings.</li>
    <li><strong>Secure Configuration</strong>: Reads <code>MONGODB_ATLAS_URI</code> from environment variables—no hardcoded credentials.</li>
    <li><strong>Extensible</strong>: Easily add POST/PUT handlers, pagination (<code>skip</code>, <code>limit</code>), filtering, Azure AD authentication, and more.</li>
  </ul>
  <hr>
  <h2>Requirements</h2>
  <ul>
    <li><strong>Python</strong> 3.9–3.12</li>
    <li><strong>Azure Functions Core Tools</strong> v4</li>
    <li><strong>VS Code</strong> with <strong>Python</strong> &amp; <strong>Azure Functions</strong> extensions</li>
    <li>A <strong>MongoDB Atlas</strong> cluster &amp; user with <strong>read</strong> or <strong>readWrite</strong> permissions</li>
    <li>An <strong>Azure Subscription</strong> and a <strong>Resource Group</strong></li>
  </ul>
  <hr>
  <h2>Local Development &amp; Testing (Anonymous)</h2>
  <ol>
    <li><strong>Clone repository</strong>
      <pre><code>git clone https://github.com/&lt;your-username&gt;/azure-mongoapi-gateway.git
cd azure-mongoapi-gateway</code></pre>
    </li>
    <li><strong>Prepare settings</strong>
      <pre><code>cp local.settings.sample.json local.settings.json</code></pre>
      <p>Edit <code>local.settings.json</code>:</p>
      <pre><code>{
  "IsEncrypted": false,
  "Values": {
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "MONGODB_ATLAS_URI": "&lt;your-atlas-connection-string&gt;"
  }
}</code></pre>
    </li>
    <li><strong>Enable anonymous auth</strong> (for local testing)<br>
      In <code>MongoApi/function.json</code>, set:
      <pre><code>- "authLevel": "function",
+ "authLevel": "anonymous",</code></pre>
    </li>
    <li><strong>Install dependencies</strong>
      <pre><code>python3 -m venv .venv
source .venv/bin/activate    # Windows PowerShell: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt</code></pre>
    </li>
    <li><strong>Run locally</strong>
      <pre><code>func start</code></pre>
    </li>
    <li><strong>Test GET calls</strong>
      <p>List documents:</p>
      <pre><code>GET http://localhost:7071/api/MongoApi?db=&lt;db&gt;&amp;coll=&lt;collection&gt;</code></pre>
      <p>Fetch one document:</p>
      <pre><code>GET http://localhost:7071/api/MongoApi?db=&lt;db&gt;&amp;coll=&lt;collection&gt;&amp;id=&lt;ObjectId&gt;</code></pre>
    </li>
  </ol>
  <hr>
  <h2>Deploying to Azure with Function-Level Authentication</h2>
  <ol>
    <li><strong>Require function-key auth</strong><br>
      In <code>MongoApi/function.json</code>, revert:
      <pre><code>- "authLevel": "anonymous",
+ "authLevel": "function",</code></pre>
    </li>
    <li><strong>Create a Function App</strong> (using VS Code)
      <ul>
        <li>Open the <strong>Azure</strong> sidebar and click <em>Create Function App</em></li>
        <li>Select your Subscription and existing Resource Group</li>
        <li>Provide a globally unique name (e.g. <code>mongoapi-gateway-func</code>)</li>
        <li>Choose <strong>Linux</strong>, <strong>Python 3.11</strong>, and <strong>Consumption</strong> plan</li>
      </ul>
    </li>
    <li><strong>Deploy your code</strong><br>
      Right-click the new Function App in VS Code → <em>Deploy to Function App</em> → select your project folder
    </li>
    <li><strong>Configure application settings</strong><br>
      In Azure Portal → Function App → <em>Configuration &gt; Application settings</em>, add:
      <table>
        <thead>
          <tr><th>Setting Name</th><th>Value</th></tr>
        </thead>
        <tbody>
          <tr><td>AzureWebJobsStorage</td><td>&lt;your-storage-connection-string&gt;</td></tr>
          <tr><td>FUNCTIONS_WORKER_RUNTIME</td><td>python</td></tr>
          <tr><td>MONGODB_ATLAS_URI</td><td>&lt;your-atlas-connection-string&gt;</td></tr>
        </tbody>
      </table>
      <p>Save and let the function restart.</p>
    </li>
    <li><strong>Retrieve your function key</strong><br>
      In VS Code’s Azure panel, expand <strong>Functions &gt; MongoApi</strong>, right-click <em>Get Function URL</em> and copy the URL including <code>?code=</code>.
    </li>
  </ol>
  <hr>
  <h2>API Usage</h2>
  <h3>Authentication</h3>
  <p>Include the function key on every request:</p>
  <ul>
    <li><strong>Query param</strong>: <code>?code=&lt;your-function-key&gt;</code></li>
    <li><strong>Header</strong>: <code>x-functions-key: &lt;your-function-key&gt;</code></li>
  </ul>
  <h3>GET Endpoints</h3>
  <ul>
    <li><strong>List documents</strong>
      <pre><code>GET https://&lt;your-app&gt;.azurewebsites.net/api/MongoApi?db=&lt;DB&gt;&amp;coll=&lt;Collection&gt;&amp;code=&lt;key&gt;</code></pre>
    </li>
    <li><strong>Fetch single document</strong>
      <pre><code>GET https://&lt;your-app&gt;.azurewebsites.net/api/MongoApi?db=&lt;DB&gt;&amp;coll=&lt;Collection&gt;&amp;id=&lt;ObjectId&gt;&amp;code=&lt;key&gt;</code></pre>
    </li>
    <li><strong>Pagination</strong> (optional)
      <pre><code>GET https://&lt;your-app&gt;.azurewebsites.net/api/MongoApi?db=&lt;DB&gt;&amp;coll=&lt;Collection&gt;&amp;skip=100&amp;limit=50&amp;code=&lt;key&gt;</code></pre>
    </li>
    <li><strong>Filtering</strong> (custom extension)
      <pre><code>GET https://&lt;your-app&gt;.azurewebsites.net/api/MongoApi?db=&lt;DB&gt;&amp;coll=&lt;Collection&gt;&amp;status=active&amp;code=&lt;key&gt;</code></pre>
    </li>
  </ul>
  <h3>POST Endpoint (Optional)</h3>
  <p>Extend the function to accept JSON bodies:</p>
  <pre><code>POST https://&lt;your-app&gt;.azurewebsites.net/api/MongoApi?db=&lt;DB&gt;&amp;coll=&lt;Collection&gt;&amp;code=&lt;key&gt;
Content-Type: application/json

{ "name": "Alice", "age": 30 }</code></pre>
  <p>Returns:</p>
  <pre><code>{ "inserted_id": "&lt;newObjectId&gt;" }</code></pre>
  <hr>
  <h2>Manual Azure Portal Deployment</h2>
  <ol>
    <li>Create a new <strong>Function App</strong> (Linux, Python, Consumption) in your Resource Group.</li>
    <li>In <strong>Deployment Center</strong>, select <strong>Local Git</strong> or <strong>ZIP Deploy</strong>.</li>
    <li>Connect and push:
      <pre><code>git remote add azure &lt;deployment-git-url&gt;
