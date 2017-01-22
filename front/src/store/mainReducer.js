import {playerReducer} from "../modules/player";
import {combineReducers} from "redux-immutable";
import {decoratedEventsReducer} from "../modules/events";
import {decoratedCharactersAroundReducer} from "../modules/charactersAround";
import {decoratedSpeechReducer} from "../modules/speech";


const mainReducer = combineReducers({
  player: playerReducer,
  events: decoratedEventsReducer,
  charactersAround: decoratedCharactersAroundReducer,
  speech: decoratedSpeechReducer,
});

export default mainReducer;
