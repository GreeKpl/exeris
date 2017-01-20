import {connect} from "react-redux";
import PlayerPage from "./PlayerPage";

const mapStateToProps = (state, ownProps) => {
  return {
    cos: ownProps.params,
  };
};

const mapDispatchToProps = (dispatch) => {
  return {}
};

const PlayerPageContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(PlayerPage);

export default PlayerPageContainer;
