import {connect} from "react-redux";
import React from "react";
import CreateCharacterPanelContainer from "./CreateCharacterPanelContainer";
import AchievementsListContainer from "./AchievementsListContainer";
import {Grid, Row, Col} from "react-bootstrap";

const Dashboard = () => {
  return <div>
    Bonvenon! It's rendered with react.
    <Grid>
      <Row className="show-grid">
        <Col xs={12} md={8}>
          <CreateCharacterPanelContainer/>
        </Col>
        <Col xs={12} md={4}>
          <AchievementsListContainer/>
        </Col>
      </Row>
    </Grid>

  </div>
};

export {Dashboard};


const mapStateToProps = (state) => {
  return {};
};

const mapDispatchToProps = (dispatch) => {
  return {}
};

const DashboardContainer = connect(
  mapStateToProps,
  mapDispatchToProps
)(Dashboard);

export default DashboardContainer;
