import React from "react";
import { BrowserBarcodeReader } from "@zxing/library";
import { Button, Typography } from "antd";
import { useHistory } from "react-router-dom";
import { getAssetIDForAssetNumber } from "../../api/asset";

function Scanner() {
  const history = useHistory();

  const ref = React.useRef();
  const codeReaderRef = React.useRef();
  const [devices, setDevices] = React.useState([]);
  const [selectedDeviceIdx, setSelectedDeviceIdx] = React.useState(undefined);

  React.useEffect(() => {
    const video = ref.current;
    if (video) {
      video.setAttribute("autoplay", "");
      video.setAttribute("muted", "");
      video.setAttribute("playsinline", "");

      navigator.mediaDevices.getUserMedia({ video: true }).then(() => {
        const bbr = new BrowserBarcodeReader(500);
        bbr
          .listVideoInputDevices()
          .then(videoInputDevices => {
            setDevices(videoInputDevices);
            setSelectedDeviceIdx(0);
          })
          .catch(err => console.error(err));
        codeReaderRef.current = bbr;
      });
    }
  }, [ref]);

  React.useEffect(() => {
    const video = ref.current;
    if (video && selectedDeviceIdx != null) {
      navigator.mediaDevices
        .getUserMedia({
          video: { deviceId: devices[selectedDeviceIdx].deviceId },
        })
        .then(stream => {
          codeReaderRef.current.decodeFromStream(stream, video, (res, err) => {
            if (!err) {
              proc(res.text);
            }
          });
        });
    }
  }, [selectedDeviceIdx]);

  function proc(text) {
    const assetNumber = parseInt(text);
    if (assetNumber) {
      getAssetIDForAssetNumber(assetNumber).then(id => {
        history.push(`/scanner/assets/${id}`);
      });
    }
  }

  function nextDevice() {
    setSelectedDeviceIdx(idx => (idx + 1) % devices.length);
  }

  return (
    <div style={{ padding: 16 }}>
      <Typography.Title level={4}>Barcode Scanner</Typography.Title>
      <video
        id="video"
        ref={ref}
        width="100%"
        controls={false}
        style={{ border: "1px solid gray" }}
      />

      <div style={{ textAlign: "center" }}>
        <Button disabled={devices.length < 2} onClick={nextDevice}>
          Toggle Device
        </Button>
      </div>
    </div>
  );
}

export default Scanner;
