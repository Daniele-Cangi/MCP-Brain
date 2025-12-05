import * as vscode from "vscode";
import fetch from "node-fetch";

export function activate(context: vscode.ExtensionContext) {
    const disposable = vscode.commands.registerCommand(
        "devBrain.runCycle",
        async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showErrorMessage(
                    "Dev Brain: No active editor. Open a file and try again."
                );
                return;
            }

            const document = editor.document;
            const workspaceFolder = vscode.workspace.getWorkspaceFolder(document.uri);
            if (!workspaceFolder) {
                vscode.window.showErrorMessage(
                    "Dev Brain: No workspace folder found. Open a folder/workspace first."
                );
                return;
            }

            const fullPath = document.uri.fsPath;
            const rootPath = workspaceFolder.uri.fsPath;
            // Compute workspace-relative path, normalize to forward slashes
            const targetFile = fullPath
                .substring(rootPath.length + 1)
                .replace(/\\/g, "/");

            const userRequest = await vscode.window.showInputBox({
                placeHolder: "Describe what you want Dev Brain to do with this file",
                prompt: "Dev Brain – user request",
            });

            if (!userRequest) {
                return; // user cancelled
            }

            const config = vscode.workspace.getConfiguration("devBrain");
            const baseUrl =
                config.get<string>("serverUrl", "http://127.0.0.1:8000");

            const url = `${baseUrl?.replace(/\/$/, "")}/run-cycle`;

            try {
                const response = await fetch(url, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        user_request: userRequest,
                        target_file: targetFile,
                        changed_files: [targetFile],
                    }),
                });

                if (!response.ok) {
                    const text = await response.text();
                    vscode.window.showErrorMessage(
                        `Dev Brain: HTTP ${response.status} – ${text}`
                    );
                    return;
                }

                const data = (await response.json()) as {
                    frame_id: string;
                    prompt: string;
                };

                const docContent = [
                    ">>> Dev Brain – Run Cycle <<<",
                    `Frame ID: ${data.frame_id}`,
                    `Target File: ${targetFile}`,
                    `User Request: ${userRequest}`,
                    "",
                    "--- PROMPT TO SEND TO CODER LLM ---",
                    data.prompt,
                ].join("\n");

                const doc = await vscode.workspace.openTextDocument({
                    content: docContent,
                    language: "markdown",
                });

                await vscode.window.showTextDocument(doc, vscode.ViewColumn.Beside);

                vscode.window.showInformationMessage(
                    `Dev Brain: frame ${data.frame_id} created.`
                );
            } catch (err: any) {
                vscode.window.showErrorMessage(
                    `Dev Brain: request failed – ${err.message ?? String(err)}`
                );
            }
        }
    );

    context.subscriptions.push(disposable);
}

export function deactivate() { }
