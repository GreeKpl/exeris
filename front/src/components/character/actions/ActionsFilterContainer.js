import {connect} from "react-redux";
import ActionsFilter from "./ActionsFilter";

const mapStateToProps = (state, ownProps) => {
  return {
    characterId: ownProps.characterId,
    filterText: "", // placeholder
  };
};

const mapDispatchToProps = (dispatch) => {
  return {}
};

const ActionsFilterContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(ActionsFilter);

export default ActionsFilterContainer;
