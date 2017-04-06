import {playerReducer} from "../modules/player";
import {combineReducers} from "redux-immutable";
import {decoratedEventsReducer} from "../modules/events";
import {decoratedCharactersAroundReducer} from "../modules/charactersAround";
import {decoratedSpeechReducer} from "../modules/speech";
import {decoratedTopPanelReducer} from "../modules/topPanel";
import {decoratedEntitiesReducer} from "../modules/entities";
import {notificationsReducer} from "../modules/notifications";
import {decoratedRecipesReducer} from "../modules/recipes";
import {reducer as formReducer} from "redux-form/immutable";
import {decoratedDynamicNamesReducer} from "../modules/dynamicNames";
import {decoratedTravelReducer} from "../modules/travel";
import {decoratedMyCharacterReducer} from "../modules/myCharacter";


const mainReducer = combineReducers({
  player: playerReducer,
  events: decoratedEventsReducer,
  charactersAround: decoratedCharactersAroundReducer,
  speech: decoratedSpeechReducer,
  topPanel: decoratedTopPanelReducer,
  entities: decoratedEntitiesReducer,
  myCharacter: decoratedMyCharacterReducer,
  notifications: notificationsReducer,
  recipes: decoratedRecipesReducer,
  travel: decoratedTravelReducer,
  dynamicNames: decoratedDynamicNamesReducer,
  form: formReducer,
});

export default mainReducer;
