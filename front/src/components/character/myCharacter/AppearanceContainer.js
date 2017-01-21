import {connect} from "react-redux";
import Appearance from "./Appearance";

const mapStateToProps = (state, ownProps) => {
  return {characterId: ownProps.characterId};
};

const mapDispatchToProps = (dispatch) => {
  return {}
};

const AppearanceContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(Appearance);

export default AppearanceContainer;
