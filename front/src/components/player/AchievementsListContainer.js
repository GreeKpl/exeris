import {connect} from "react-redux";
import {requestAchievementsList, getAchievementsList} from "../../modules/player";
import AchievementsList from "./AchievementsList";

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
