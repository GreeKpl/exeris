import {connect} from "react-redux";
import ActionsPage from "./ActionsPage";

const mapStateToProps = (state, ownProps) => {
  return {
    characterId: ownProps.params.characterId,
    isSmall: state.get("browser").atMost.small,
  };
};

const mapDispatchToProps = (dispatch) => {
  return {}
};

const ActionsPageContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(ActionsPage);

export default ActionsPageContainer;
