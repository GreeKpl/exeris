import {ThunkDispatch} from "redux-thunk";
import {RootStateOrAny} from "react-redux";
import {AnyAction} from "redux";

export interface SocketIO extends SocketIOClient.Socket {
  request(eventName: string, ...args: any[]): void;
  reconnect(): void;
}

export type Dispatch = ThunkDispatch<RootStateOrAny, SocketIO, AnyAction>;

