/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { rpc } from "@web/core/network/rpc";

class CancelCreate extends Component {
  static template = "AutoloadSolution.CancelCreate";

  setup() {
    this.state = useState({
      date: "",
      vehicleNumber: "",
      ownerName: "",
      mileage: "",
      address: "",
      fuelType: "",
      vehicleWeight: "",
      dealer: "",
      chassisNumber: "",
      residentNumber: "",
      uploadedImage: null,
    });
  }

  handleInputChange(field, value) {
    this.state[field] = value;
  }

  async handleSubmit(ev) {
    ev.preventDefault();

    const payload = {
      date: this.state.date,
      vehicle_number: this.state.vehicleNumber,
      owner_name: this.state.ownerName,
      mileage: this.state.mileage,
      address: this.state.address,
      fuel_type: this.state.fuelType,
      vehicle_weight: this.state.vehicleWeight,
      dealer: this.state.dealer,
      chassis_number: this.state.chassisNumber,
      resident_number: this.state.residentNumber,
    };

    try {
      await rpc("/autoloadsolution/cancel/submit", payload);
      alert("말소 정보가 성공적으로 저장되었습니다.");
      this.handleReset();
    } catch (error) {
      console.error("저장 실패:", error);
      alert("오류가 발생했습니다. 콘솔을 확인해주세요.");
    }
  }

  handleReset() {
    Object.assign(this.state, {
      date: "",
      vehicleNumber: "",
      ownerName: "",
      mileage: "",
      address: "",
      fuelType: "",
      vehicleWeight: "",
      dealer: "",
      chassisNumber: "",
      residentNumber: "",
      uploadedImage: null,
    });
  }

  handleImageUpload() {
    document.getElementById("imageUpload")?.click();
  }

  handleImageChange(ev) {
    const file = ev.target.files && ev.target.files[0];
    if (file) {
      this.state.uploadedImage = file;
      alert(`이미지가 업로드되었습니다: ${file.name}`);
    }
  }
}

registry
  .category("actions")
  .add("AutoloadSolution.cancel_create", CancelCreate);
