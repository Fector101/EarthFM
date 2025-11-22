package org.tdynamos.earthfm;

import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothHidDevice;
import android.bluetooth.BluetoothHidDeviceAppSdpSettings;
import android.bluetooth.BluetoothProfile;

import android.content.Context;
import android.content.Intent;

import android.util.Log;

import java.util.concurrent.Executor;
import java.util.concurrent.Executors;

public class HidService {

    private static final String TAG = "python";

    private BluetoothAdapter adapter;
    private BluetoothHidDevice hidDevice;
    private BluetoothDevice host;

    private final Executor executor =
        Executors.newSingleThreadExecutor();

    // ---------------- Constructor ----------------

    public HidService(Context ctx) {

        adapter = BluetoothAdapter.getDefaultAdapter();

        if (adapter == null) {
            Log.d(TAG, "No Bluetooth adapter");
            return;
        }

        if (!adapter.isEnabled()) {
            Log.d(TAG, "Bluetooth disabled");
            return;
        }

        // Set visible name
        adapter.setName("Python HID");

        // Ask user for discoverable mode
        Intent discoverableIntent =
            new Intent(BluetoothAdapter.ACTION_REQUEST_DISCOVERABLE);

        discoverableIntent.putExtra(
            BluetoothAdapter.EXTRA_DISCOVERABLE_DURATION,
            300
        );

        discoverableIntent.addFlags(
            Intent.FLAG_ACTIVITY_NEW_TASK
        );

        ctx.startActivity(discoverableIntent);

        // Request HID profile
        adapter.getProfileProxy(
            ctx,
            serviceListener,
            BluetoothProfile.HID_DEVICE
        );
    }

    // ---------------- HID Descriptor ----------------

    private static final byte[] DESCRIPTOR = new byte[]{
        (byte)0x05,(byte)0x01,
        (byte)0x09,(byte)0x06,
        (byte)0xA1,(byte)0x01,

        (byte)0x05,(byte)0x07,
        (byte)0x19,(byte)0xE0,
        (byte)0x29,(byte)0xE7,

        (byte)0x15,(byte)0x00,
        (byte)0x25,(byte)0x01,
        (byte)0x75,(byte)0x01,
        (byte)0x95,(byte)0x08,
        (byte)0x81,(byte)0x02,

        (byte)0x95,(byte)0x01,
        (byte)0x75,(byte)0x08,
        (byte)0x81,(byte)0x01,

        (byte)0x95,(byte)0x06,
        (byte)0x75,(byte)0x08,
        (byte)0x15,(byte)0x00,
        (byte)0x25,(byte)0x65,
        (byte)0x05,(byte)0x07,
        (byte)0x19,(byte)0x00,
        (byte)0x29,(byte)0x65,
        (byte)0x81,(byte)0x00,

        (byte)0xC0
    };

    // ---------------- Service Listener ----------------

    private final BluetoothProfile.ServiceListener
        serviceListener =
        new BluetoothProfile.ServiceListener() {

        @Override
        public void onServiceConnected(
            int profile,
            BluetoothProfile proxy
        ) {
            hidDevice = (BluetoothHidDevice) proxy;
            Log.d(TAG, "HID profile ready");
            registerApp();
        }

        @Override
        public void onServiceDisconnected(int profile) {
            Log.d(TAG, "HID profile disconnected");
        }
    };

    // ---------------- HID Callback ----------------

    private final BluetoothHidDevice.Callback
        callback =
        new BluetoothHidDevice.Callback() {

        @Override
        public void onConnectionStateChanged(
            BluetoothDevice device,
            int state
        ) {
            Log.d(TAG, "Connection state=" + state);

            if (state == BluetoothProfile.STATE_CONNECTED) {
                host = device;
                Log.d(TAG, "Host connected");
            }

            if (state ==
                BluetoothProfile.STATE_DISCONNECTED) {
                host = null;
                Log.d(TAG, "Host disconnected");
            }
        }
    };

    // ---------------- Register HID ----------------

    private void registerApp() {

        BluetoothHidDeviceAppSdpSettings sdp =
            new BluetoothHidDeviceAppSdpSettings(
                "Python HID",
                "Python Keyboard",
                "Python",
                (byte)0x40,
                DESCRIPTOR
            );

        boolean ok =
            hidDevice.registerApp(
                sdp,
                null,
                null,
                executor,
                callback
            );

        Log.d(TAG, "registerApp=" + ok);
    }

    // ---------------- API for Python ----------------

    public void sendKey(int usage) {

        if (hidDevice == null || host == null) {
            Log.d(TAG, "sendKey ignored");
            return;
        }

        byte[] report = new byte[8];
        report[2] = (byte) usage;

        hidDevice.sendReport(host, 0, report);
        hidDevice.sendReport(host, 0, new byte[8]);
    }

    public boolean isReady() {
        return hidDevice != null;
    }
}

