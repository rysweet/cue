"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.StatusBarManager = void 0;
const vscode = __importStar(require("vscode"));
class StatusBarManager {
    constructor() {
        this.statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
        this.statusBarItem.command = 'blarifyVisualizer.showVisualization';
        this.statusBarItem.show();
    }
    setStatus(text, icon) {
        const iconPrefix = icon ? `$(${icon}) ` : '';
        this.statusBarItem.text = `${iconPrefix}Blarify: ${text}`;
        this.statusBarItem.tooltip = `Blarify Visualizer\n${text}\nClick to open visualization`;
    }
    setBusy(text = 'Working...') {
        this.setStatus(text, 'sync~spin');
    }
    setReady(text = 'Ready') {
        this.setStatus(text, 'check');
    }
    setError(text) {
        this.setStatus(text, 'error');
        this.statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.errorBackground');
        // Clear error background after 5 seconds
        setTimeout(() => {
            this.statusBarItem.backgroundColor = undefined;
        }, 5000);
    }
    setWarning(text) {
        this.setStatus(text, 'warning');
        this.statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.warningBackground');
        // Clear warning background after 5 seconds
        setTimeout(() => {
            this.statusBarItem.backgroundColor = undefined;
        }, 5000);
    }
    dispose() {
        this.statusBarItem.dispose();
    }
}
exports.StatusBarManager = StatusBarManager;
//# sourceMappingURL=statusBarManager.js.map