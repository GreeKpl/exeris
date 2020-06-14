import {Dispatch} from "../store/types";
import {browserHistory} from "react-router";
import { History } from "history";

export const setUpSocketioListeners = (dispatch: Dispatch, socket: SocketIOClient.Socket) => {
  socket.on("player.not_logged_in", () => {
    dispatch(logout(browserHistory));
  });
}

export const login = (email: string, password: string, history: any) => {
  return async (dispatch: Dispatch, getState: any, socket: SocketIOClient.Socket) => {
    const response = await fetch("/login", {
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
      socket.disconnect();
      socket.connect();

      history.push("/player");
    }
  }
};

export const logout = (history: History) => {
  return async (dispatch: any, getState: any, socket: SocketIOClient.Socket) => {
    const response = await fetch("/logout", {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      }
    });
    if (response.ok) {
      socket.disconnect();
      socket.connect();

      history.push("/login");
    }
  }
};

