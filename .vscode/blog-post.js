// File: .vscode/blog-post.js
const vscode = require("vscode");
const fs = require("fs");
const path = require("path");

/**
 * @param {vscode.ExtensionContext} context
 */
function activate(context) {
  let disposable = vscode.commands.registerCommand(
    "blog.createPost",
    async () => {
      try {
        // Get the workspace folder
        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (!workspaceFolder) {
          throw new Error("No workspace folder found");
        }

        // Get user input for the post title
        const postTitle = await vscode.window.showInputBox({
          prompt: "Enter the blog post title",
          placeHolder: "my-awesome-post",
          validateInput: (text) => {
            return /^[a-zA-Z0-9-]+$/.test(text)
              ? null
              : "Title can only contain letters, numbers, and hyphens";
          },
        });

        if (!postTitle) {
          return; // User cancelled
        }

        // Create the date string in YYYY-MM-DD format
        const date = new Date().toISOString().split("T")[0];

        // Create filename
        const fileName = `${date}_${postTitle}.md`;

        // Ensure _posts directory exists
        const postsDir = path.join(workspaceFolder.uri.fsPath, "_posts");
        if (!fs.existsSync(postsDir)) {
          fs.mkdirSync(postsDir, { recursive: true });
        }

        // Create full file path
        const filePath = path.join(postsDir, fileName);

        // Generate initial content with frontmatter
        const initialContent = `---
title: ${postTitle.replace(/-/g, " ")}
date: ${date}
categories: []
tags: []
---

# ${postTitle.replace(/-/g, " ")}

`;

        // Create the file
        fs.writeFileSync(filePath, initialContent);

        // Open the new file in the editor
        const doc = await vscode.workspace.openTextDocument(filePath);
        await vscode.window.showTextDocument(doc);

        // Show success message
        vscode.window.showInformationMessage(
          `Created new blog post: ${fileName}`
        );
      } catch (error) {
        vscode.window.showErrorMessage(
          `Error creating blog post: ${error.message}`
        );
      }
    }
  );

  context.subscriptions.push(disposable);
}

function deactivate() {}

module.exports = {
  activate,
  deactivate,
};
