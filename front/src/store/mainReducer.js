import {playerReducer} from "../modules/player";
import {combineReducers} from "redux-immutable";
import {decoratedEventsReducer} from "../modules/events";


const mainReducer = combineReducers({
  player: playerReducer,
  events: decoratedEventsReducer,
});

export default mainReducer;
