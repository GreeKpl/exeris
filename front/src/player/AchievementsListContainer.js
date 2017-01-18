import {connect} from "react-redux";
import {requestAchievementsList} from "./actions";
import AchievementsList from "./AchievementsList";
import {getAchievementsList} from "./reducers";

const mapStateToProps = (state) => {
  return {achievements: getAchievementsList(state.get("player"))};
};

const mapDispatchToProps = (dispatch) => {
  return {
    onMount: () => dispatch(requestAchievementsList()),
  }
};

const AchievementsListContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(AchievementsList);

export default AchievementsListContainer;
