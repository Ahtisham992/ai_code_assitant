const vscode = require('vscode');
const axios = require('axios');

/**
 * @param {vscode.ExtensionContext} context
 */
function activate(context) {
    console.log('AI Code Assistant extension is now active!');

    // Get server URL from settings
    function getServerUrl() {
        const config = vscode.workspace.getConfiguration('aiCodeAssistant');
        return config.get('serverUrl', 'http://localhost:5000');
    }

    // Get selected code or entire document
    function getSelectedCode() {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showErrorMessage('No active editor found!');
            return null;
        }

        const selection = editor.selection;
        const selectedText = editor.document.getText(selection);
        
        if (selectedText) {
            return { code: selectedText, selection: selection };
        } else {
            // If no selection, use entire document
            const fullText = editor.document.getText();
            return { code: fullText, selection: null };
        }
    }

    // Show result in output or replace selection
    async function showResult(result, feature, originalSelection) {
        const config = vscode.workspace.getConfiguration('aiCodeAssistant');
        const showInNewEditor = config.get('showInNewEditor', false);
        const editor = vscode.window.activeTextEditor;

        if (!editor) return;

        if (feature === 'explain' || feature === 'document') {
            // Show explanation/documentation in new document
            const doc = await vscode.workspace.openTextDocument({
                content: result.output,
                language: 'markdown'
            });
            await vscode.window.showTextDocument(doc, vscode.ViewColumn.Beside);
        } else if (feature === 'fix' || feature === 'optimize') {
            // For code modifications
            const output = result.output;
            const explanation = result.explanation || result.suggestions?.join('\n\n') || '';

            if (showInNewEditor) {
                // Show in new editor
                const doc = await vscode.workspace.openTextDocument({
                    content: output,
                    language: editor.document.languageId
                });
                await vscode.window.showTextDocument(doc, vscode.ViewColumn.Beside);
                
                // Show explanation in output channel
                if (explanation) {
                    const outputChannel = vscode.window.createOutputChannel('AI Assistant');
                    outputChannel.clear();
                    outputChannel.appendLine('='.repeat(60));
                    outputChannel.appendLine(feature === 'fix' ? '🔧 Bug Fix Explanation' : '⚡ Optimization Details');
                    outputChannel.appendLine('='.repeat(60));
                    outputChannel.appendLine(explanation);
                    outputChannel.show(true);
                }
            } else {
                // Replace selection with fixed/optimized code
                if (originalSelection) {
                    await editor.edit(editBuilder => {
                        editBuilder.replace(originalSelection, output);
                    });
                    vscode.window.showInformationMessage(
                        `✅ Code ${feature === 'fix' ? 'fixed' : 'optimized'} successfully!`
                    );
                } else {
                    // If no selection, show in new editor
                    const doc = await vscode.workspace.openTextDocument({
                        content: output,
                        language: editor.document.languageId
                    });
                    await vscode.window.showTextDocument(doc, vscode.ViewColumn.Beside);
                }
            }
        } else if (feature === 'test') {
            // Show tests in new editor
            const doc = await vscode.workspace.openTextDocument({
                content: result.output,
                language: 'python'
            });
            await vscode.window.showTextDocument(doc, vscode.ViewColumn.Beside);
        }
    }

    // Generic function to call AI backend
    async function callAIAssistant(feature, featureName) {
        const codeData = getSelectedCode();
        if (!codeData) return;

        const { code, selection } = codeData;

        // Show progress
        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: `AI Assistant: ${featureName}...`,
            cancellable: false
        }, async (progress) => {
            try {
                const serverUrl = getServerUrl();
                
                // Check if server is running
                try {
                    await axios.get(`${serverUrl}/api/status`);
                } catch (error) {
                    vscode.window.showErrorMessage(
                        `Cannot connect to AI Assistant server at ${serverUrl}. Please start the server first.`
                    );
                    return;
                }

                progress.report({ message: 'Processing your code...' });

                // Call API
                const response = await axios.post(`${serverUrl}/api/process`, {
                    code: code,
                    feature: feature,
                    use_context: true
                });

                if (response.data.success) {
                    await showResult(response.data.result, feature, selection);
                } else {
                    vscode.window.showErrorMessage(`Error: ${response.data.error}`);
                }
            } catch (error) {
                vscode.window.showErrorMessage(
                    `AI Assistant Error: ${error.message}`
                );
                console.error('Extension error:', error);
            }
        });
    }

    // Register commands
    const commands = [
        {
            id: 'aiCodeAssistant.explain',
            name: 'Explaining code',
            feature: 'explain'
        },
        {
            id: 'aiCodeAssistant.document',
            name: 'Generating documentation',
            feature: 'document'
        },
        {
            id: 'aiCodeAssistant.fixBug',
            name: 'Fixing bugs',
            feature: 'fix'
        },
        {
            id: 'aiCodeAssistant.optimize',
            name: 'Optimizing code',
            feature: 'optimize'
        },
        {
            id: 'aiCodeAssistant.generateTests',
            name: 'Generating tests',
            feature: 'test'
        }
    ];

    commands.forEach(cmd => {
        const disposable = vscode.commands.registerCommand(cmd.id, () => {
            callAIAssistant(cmd.feature, cmd.name);
        });
        context.subscriptions.push(disposable);
    });

    // Status bar item
    const statusBarItem = vscode.window.createStatusBarItem(
        vscode.StatusBarAlignment.Right,
        100
    );
    statusBarItem.text = '$(robot) AI Assistant';
    statusBarItem.tooltip = 'AI Code Assistant is ready';
    statusBarItem.show();
    context.subscriptions.push(statusBarItem);
}

function deactivate() {}

module.exports = {
    activate,
    deactivate
};
