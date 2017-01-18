import * as actions from "../player/actions";
import * as Immutable from "immutable";

export const ownCharactersListReducer = (state = Immutable.List(), action) => {
  switch (action.type) {
    case actions.UPDATE_OWN_CHARACTERS_LIST:
      return Immutable.fromJS(action.charactersList);
    default:
      return state;
  }
};

export const getOwnCharactersList = state => state.get("ownCharactersList");

export const playerReducer = (state = Immutable.fromJS({"achievements": []}), action) => {
  switch (action.type) {
    case actions.UPDATE_ACHIEVEMENTS_LIST:
      return state.set("achievements", Immutable.fromJS(action.achievementsList));
    default:
      return state;
  }
};

export const getAchievementsList = state => {
  return state.get("achievements");
};
