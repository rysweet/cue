"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.createLogger = createLogger;
const winston_1 = __importDefault(require("winston"));
function createLogger(debug = false) {
    const winstonLogger = winston_1.default.createLogger({
        level: debug ? 'debug' : 'info',
        format: winston_1.default.format.combine(winston_1.default.format.timestamp(), winston_1.default.format.errors({ stack: true }), winston_1.default.format.json()),
        defaultMeta: { service: 'neo4j-container-manager' },
        transports: [
            new winston_1.default.transports.Console({
                format: winston_1.default.format.combine(winston_1.default.format.colorize(), winston_1.default.format.simple()),
            }),
        ],
    });
    return {
        debug(message, meta) {
            winstonLogger.debug(message, meta);
        },
        info(message, meta) {
            winstonLogger.info(message, meta);
        },
        warn(message, meta) {
            winstonLogger.warn(message, meta);
        },
        error(message, meta) {
            winstonLogger.error(message, meta);
        },
    };
}
//# sourceMappingURL=logger.js.map