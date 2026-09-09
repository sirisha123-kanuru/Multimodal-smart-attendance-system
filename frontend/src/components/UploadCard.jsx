import { useState } from "react";

function UploadCard({
  title,
  accept,
  onFileSelect,
}) {

  const [fileName, setFileName] =
    useState("No video selected");

  const handleChange = (e) => {

    const file = e.target.files[0];

    if (file) {

      setFileName(file.name);

      if (onFileSelect) {
        onFileSelect(file);
      }

    }

  };

  return (

    <div className="upload-card">

      <h3>{title}</h3>

      <label className="upload-btn">

        Choose Video

        <input
          type="file"
          accept={accept}
          onChange={handleChange}
          hidden
        />

      </label>

      <p className="file-name">

        {fileName}

      </p>

    </div>

  );

}

export default UploadCard;