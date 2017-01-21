import {connect} from "react-redux";
import MapInfo from "./MapInfo";

const mapStateToProps = (state, ownProps) => {
  return {characterId: ownProps.characterId};
};

const mapDispatchToProps = (dispatch) => {
  return {}
};

const MapInfoContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(MapInfo);

export default MapInfoContainer;
