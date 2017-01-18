import * as actions from "../player/actions";
import * as Immutable from "immutable";

const playerReducer = (state = Immutable.fromJS({"achievements": []}), action) => {
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

export default playerReducer;
