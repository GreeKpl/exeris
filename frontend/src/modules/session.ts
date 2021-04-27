import {Dispatch, SocketIO} from "../store/types";
import { History } from "history";

export const setUpSocketioListeners = (dispatch: Dispatch, socket: SocketIO, history: History) => {
  socket.on("player.not_logged_in", () => {
    // @ts-ignore
    dispatch(logout(history));
  });
}

export const login = (email: string, password: string, history: History) => {
  return async (dispatch: Dispatch, getState: any, socket: SocketIO) => {
    const response = await fetch("/api/login", {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email,
        password,
      }),
    });
    if (response.ok) {
      socket.reconnect();

      history.push("/player");
    }
  }
};

export const logout = (history: History) => {
  return async (dispatch: any, getState: any, socket: SocketIO) => {
    const response = await fetch("/api/logout", {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      }
    });
    if (response.ok) {
      socket.reconnect();

      history.push("/login");
    }
  }
};

