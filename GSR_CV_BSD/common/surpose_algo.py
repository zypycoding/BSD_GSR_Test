# #!/usr/bin/env python
# # -*- coding:utf-8 -*-
import json, os
import cv2

font = cv2.FONT_HERSHEY_SIMPLEX


def get_files_list(path,keywords):
    files_list = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(keywords):
                file_path = os.path.join(root, file)
                files_list.append(file_path)
    return files_list


def surpose_algo_result(video_path):
    """
        对字段 'mres_person' 算法结果进行处理
        算法结果是由testbed回灌得到与 '.mp4'同名的 '.txt' 文件
    """
    mp4_path = video_path
    txt_path = video_path.replace('.mp4', '.txt')
    result_path = video_path.replace('.mp4', '.avi')
    txt_result = open(txt_path).readlines()

    cap = cv2.VideoCapture(mp4_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')  # AVI格式
    result_video = cv2.VideoWriter(result_path, fourcc, fps, (width, height))

    frame_index = 0
    while cap.isOpened():
        # cap.read()按帧读取视频， 其中ret是布尔值，如果读取帧是正确的则返回True，如果文件读取到结尾，它的返回值就为False
        # frame就是每一帧的图像，是个三维矩阵。
        ret, frame = cap.read()
        if not ret:
            # print(' can not receive frame,exiting ...')
            print('{} 处理完成'.format(mp4_path))
            break
        try:
            algo_result_index = json.loads(txt_result[frame_index]).get('mres_person',[])
        except IndexError as I:
            print("视频叠加到最后一帧")
            print(I)
        for algo_result_e in algo_result_index:
            mres_rect = algo_result_e.get('mres_rect')
            mres_rect_point = mres_rect.split(',')
            point_l = (int(mres_rect_point[0]), int(mres_rect_point[1]))
            point_r = (int(mres_rect_point[2]), int(mres_rect_point[3]))
            cv2.rectangle(frame, point_l, point_r, (0, 255, 0), 1)
            id = algo_result_e.get('mres_id')
            attr = algo_result_e.get('mres_attr')
            state = algo_result_e.get('mv_state')
            Lon = round(algo_result_e.get('f32LongDistance'),2)
            Lat = round(algo_result_e.get('f32LatDistance'),2)
            VLon = round(algo_result_e.get('f32AbsoluteLongVelocity'),2)
            Vlat = round(algo_result_e.get('f32AbsoluteLatVelocity'),2)
            Score = round(algo_result_e.get('obj_score'), 2)
            zicheLongVel = round(algo_result_e.get('zicheLongVel'),2)

            info_list = f'{id}_{attr}_{state}_{Lon}_{Lat}_{VLon}_{Vlat}_{Score}_{zicheLongVel}'
            # info_list = f'{id}_{attr}_{state}_{Lon}_{Lat}_{zicheLongVel}'
            cv2.putText(frame, info_list, point_l, font, 0.5, (255, 255, 255), 1)

        info_frame_id = f'frame_id:{frame_index}'
        info_show = 'id_attr_state_LongDis_LatDise_AbsLongVel_AbsLatVel_Score_zicheLongVel'
        cv2.putText(frame, info_frame_id, (10, 30), font, 1, (255, 255, 0), 2)
        cv2.putText(frame, info_show, (10, 60), font, 1, (255, 255, 0), 2)

        result_video.write(frame)
        frame_index = frame_index + 1

    cap.release()
    result_video.release()


if __name__ == '__main__':
    result_path = r'\\Ybb9801-02810\测试记录\扬州VAN\159\自行车'
    files_list = get_files_list(result_path, '.mp4')

    for video_path in files_list:
        surpose_algo_result(video_path)
