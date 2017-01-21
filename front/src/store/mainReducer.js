import {playerReducer} from "../modules/player";
import {combineReducers} from "redux-immutable";
import {decoratedEventsReducer} from "../modules/events";
import {decoratedCharactersAroundReducer} from "../modules/charactersAround";


const mainReducer = combineReducers({
  player: playerReducer,
  events: decoratedEventsReducer,
  charactersAround: decoratedCharactersAroundReducer,
});

export default mainReducer;
