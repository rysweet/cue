import winston from 'winston';
import { Logger } from './types';

export function createLogger(debug: boolean = false): Logger {
  const winstonLogger = winston.createLogger({
    level: debug ? 'debug' : 'info',
    format: winston.format.combine(
      winston.format.timestamp(),
      winston.format.errors({ stack: true }),
      winston.format.json()
    ),
    defaultMeta: { service: 'neo4j-container-manager' },
    transports: [
      new winston.transports.Console({
        format: winston.format.combine(
          winston.format.colorize(),
          winston.format.simple()
        ),
      }),
    ],
  });
  
  return {
    debug(message: string, meta?: any) {
      winstonLogger.debug(message, meta);
    },
    info(message: string, meta?: any) {
      winstonLogger.info(message, meta);
    },
    warn(message: string, meta?: any) {
      winstonLogger.warn(message, meta);
    },
    error(message: string, meta?: any) {
      winstonLogger.error(message, meta);
    },
  };
}