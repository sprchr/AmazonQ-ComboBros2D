// @ts-nocheck
import { io } from "socket.io-client";

export const socket = io("http://localhost:3001");
// For production, change the URL to your deployed Socket.IO server