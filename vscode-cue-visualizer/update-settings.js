const fs = require('fs');
const path = require('path');
const os = require('os');

// Read .env file
const envPath = path.join(__dirname, '..', '.env');
const envContent = fs.readFileSync(envPath, 'utf8');
const envVars = {};

// Parse .env file
envContent.split('\n').forEach(line => {
    if (line && !line.startsWith('#')) {
        const [key, value] = line.split('=');
        if (key && value) {
            envVars[key.trim()] = value.trim();
        }
    }
});

// Extract Azure OpenAI endpoint parts
const endpoint = envVars.AZURE_OPENAI_ENDPOINT || '';
const endpointMatch = endpoint.match(/https:\/\/([^\/]+)\.openai\.azure\.com/);
const azureEndpoint = endpointMatch ? `https://${endpointMatch[1]}.openai.azure.com/` : '';

// Prepare settings
const settings = {
    "blarifyVisualizer.azureOpenAI.apiKey": envVars.AZURE_OPENAI_KEY || "",
    "blarifyVisualizer.azureOpenAI.endpoint": azureEndpoint,
    "blarifyVisualizer.azureOpenAI.deploymentName": envVars.AZURE_OPENAI_MODEL_CHAT || "gpt-4",
    "blarifyVisualizer.neo4j.uri": "bolt://localhost:7687", // Use blarify-neo4j container port
    "blarifyVisualizer.neo4j.username": envVars.NEO4J_USER || "neo4j",
    "blarifyVisualizer.neo4j.password": envVars.NEO4J_PASSWORD || ""
};

// VS Code settings paths
const settingsPaths = [
    // macOS - VS Code Insiders
    path.join(os.homedir(), 'Library', 'Application Support', 'Code - Insiders', 'User', 'settings.json'),
    // macOS - VS Code
    path.join(os.homedir(), 'Library', 'Application Support', 'Code', 'User', 'settings.json'),
    // Linux - VS Code Insiders
    path.join(os.homedir(), '.config', 'Code - Insiders', 'User', 'settings.json'),
    // Linux - VS Code
    path.join(os.homedir(), '.config', 'Code', 'User', 'settings.json'),
    // Windows - VS Code Insiders
    path.join(os.homedir(), 'AppData', 'Roaming', 'Code - Insiders', 'User', 'settings.json'),
    // Windows - VS Code
    path.join(os.homedir(), 'AppData', 'Roaming', 'Code', 'User', 'settings.json')
];

// Find the existing settings file
let settingsPath = null;
for (const p of settingsPaths) {
    if (fs.existsSync(p)) {
        settingsPath = p;
        break;
    }
}

if (!settingsPath) {
    console.error('Could not find VS Code settings.json file');
    console.log('Please add these settings manually to your VS Code settings:');
    console.log(JSON.stringify(settings, null, 2));
    process.exit(1);
}

// Read existing settings
let existingSettings = {};
try {
    const content = fs.readFileSync(settingsPath, 'utf8');
    existingSettings = JSON.parse(content);
} catch (e) {
    console.log('No existing settings found, creating new file');
}

// Merge settings
const updatedSettings = {
    ...existingSettings,
    ...settings
};

// Write back
try {
    fs.writeFileSync(settingsPath, JSON.stringify(updatedSettings, null, 4));
    console.log('✅ VS Code settings updated successfully!');
    console.log('Settings written to:', settingsPath);
    console.log('\nSettings added:');
    Object.entries(settings).forEach(([key, value]) => {
        // Hide sensitive parts of the API key
        if (key.includes('apiKey') || key.includes('password')) {
            const hidden = value.substring(0, 4) + '****' + value.substring(value.length - 4);
            console.log(`  ${key}: ${hidden}`);
        } else {
            console.log(`  ${key}: ${value}`);
        }
    });
    console.log('\nPlease reload VS Code for the settings to take effect.');
} catch (e) {
    console.error('Failed to write settings:', e);
    console.log('\nPlease add these settings manually to your VS Code settings:');
    console.log(JSON.stringify(settings, null, 2));
}