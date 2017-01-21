import {connect} from "react-redux";
import SkillsList from "./SkillsList";

const mapStateToProps = (state, ownProps) => {
  return {characterId: ownProps.characterId};
};

const mapDispatchToProps = (dispatch) => {
  return {}
};

const SkillsListContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(SkillsList);

export default SkillsListContainer;
