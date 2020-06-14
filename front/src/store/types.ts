import {ThunkDispatch} from "redux-thunk";
import {RootStateOrAny} from "react-redux";
import {AnyAction} from "redux";

export type Dispatch = ThunkDispatch<RootStateOrAny, SocketIOClient.Socket, AnyAction>;
